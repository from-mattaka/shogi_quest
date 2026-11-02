"""将棋クエスト履歴検索β（https://c-loft.com/shogi/quest/）からの履歴・CSA 取得。

画面の <table> は JavaScript が描画しており静的 HTML には中身が無いため、
画面が内部で呼んでいる JSON API を直接利用する。

  履歴: GET {api_base}/history/?userId={user}&gtype={gtype}
        → {"userId", "gtype", "games": [{id, created, players[2], finalStatus, length, handicap?}, ...]}
           players[0] が先手、players[1] が後手。最新 30 局のみ返る。
  棋譜: GET {api_base}/history/download/?id={game_id}   → CSA テキスト（UTF-8）
"""
from __future__ import annotations

import logging
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import requests

log = logging.getLogger(__name__)
JST = timezone(timedelta(hours=9))

def build_headers(interval: float) -> dict[str, str]:
    """ブラウザを偽装せず、自動収集ツールであることと連絡先（リポジトリ URL）を正直に名乗る。"""
    repo = os.environ.get("GITHUB_REPOSITORY")
    contact = f"https://github.com/{repo}" if repo else "personal use"
    return {
        "User-Agent": f"shogi-quest-collector/1.0 (+{contact}; personal game archive, max 1 req/{interval:g}s)",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ja,en-US;q=0.9",
    }


# 「名前(1500)」→ ("名前", 1500)。CSA の N+/N- 行もこの形式
NAME_RATING_RE = re.compile(r"^\s*(.*?)\s*[\(（]\s*(\d+)\s*[\)）]\s*$")
CSA_MOVE_RE = re.compile(r"^[+-]\d{4}[A-Z]{2}")
GAME_ID_RE = re.compile(r"^[0-9A-Za-z_-]{4,64}$")

HANDICAP_LABELS = {
    None: "平手", "": "平手",
    "KYO": "香落ち", "KAKU": "角落ち", "HISHA": "飛車落ち",
    "HIKYO": "飛香落ち", "2MAI": "二枚落ち",
}
# finalStatus のコロン以降 → 終局理由
END_REASON_LABELS = {
    "RESIGN": "投了", "TIMEUP": "時間切れ", "MATE": "詰み", "TRY": "トライ",
    "DISCONNECT": "切断", "REPETITION": "千日手", "ILLEGAL": "反則",
    "PERPETUAL_CHECK": "連続王手千日手",
}


@dataclass
class Player:
    id: str
    name: str
    rating: int | None


@dataclass
class GameEntry:
    game_id: str
    time_mode: str
    played_at: str          # JST 'YYYY-MM-DD HH:MM:SS'
    handicap: str
    sente: Player
    gote: Player
    final_status: str       # 例 'LOSE:RESIGN'
    length: int             # API の手数（投了等の終局アクションを 1 手として含む）
    end_reason: str

    def winner(self) -> str | None:
        """'SENTE' / 'GOTE' / 'DRAW' / None。

        finalStatus は「length 手目を指す側」視点の結果（サイトの history.js と同じ解釈）。
        length が奇数なら先手、偶数なら後手の視点。
        """
        kind = self.final_status.split(":", 1)[0]
        if kind == "DRAW":
            return "DRAW"
        subject = "SENTE" if self.length % 2 == 1 else "GOTE"
        other = "GOTE" if subject == "SENTE" else "SENTE"
        if kind == "WIN":
            return subject
        if kind == "LOSE":
            return other
        return None


def split_name_rating(text: str) -> tuple[str, int | None]:
    """'名前(1500)' を ('名前', 1500) に分離。レート表記がなければ (text, None)。"""
    text = (text or "").strip()
    m = NAME_RATING_RE.match(text)
    return (m.group(1).strip(), int(m.group(2))) if m else (text, None)


def utc_iso_to_jst(text: str) -> str:
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return dt.astimezone(JST).strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, AttributeError):
        return text or ""


def end_reason_from_status(status: str) -> str:
    code = status.split(":", 1)[1] if ":" in status else status
    return END_REASON_LABELS.get(code, code)


def count_csa_moves(csa_text: str) -> int:
    return sum(1 for line in csa_text.splitlines() if CSA_MOVE_RE.match(line.strip()))


class QuestFetcher:
    def __init__(self, config: dict):
        self.cfg = config
        self.api_base = config["api_base"].rstrip("/")
        self.timeout = config.get("timeout_sec", 30)
        self.retry_wait = config.get("retry_wait_sec", 3)
        self.interval = max(1.0, float(config.get("request_interval_sec", 2)))
        self._last_request = 0.0
        self.session = requests.Session()
        self.session.headers.update(build_headers(self.interval))

    def _get(self, url: str, **kwargs) -> requests.Response:
        """全リクエストの共通入口。呼び出し側がどうループしても、前回のリクエストから
        request_interval_sec（最低1秒）空けてから送信する。"""
        wait = self._last_request + self.interval - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        try:
            resp = self.session.get(url, timeout=self.timeout, **kwargs)
        finally:
            self._last_request = time.monotonic()
        resp.raise_for_status()
        return resp

    # ------------------------------------------------------------ 履歴
    def fetch_history(self, user_id: str, time_mode: str, gtype: str) -> list[GameEntry]:
        """新しい順の対局リストを返す。"""
        resp = self._get(
            f"{self.api_base}/history/",
            params={"userId": user_id.lower(), "gtype": gtype},
        )
        try:
            data = resp.json()
        except ValueError as e:
            raise RuntimeError(f"履歴 API が JSON 以外を返しました: {resp.text[:200]!r}") from e

        games = []
        for g in data.get("games") or []:
            try:
                games.append(self._parse_game(g, time_mode))
            except (KeyError, IndexError, TypeError, ValueError) as e:
                log.warning("[%s] 解析できない対局をスキップ: %s (%s)", time_mode, g.get("id"), e)
        games.sort(key=lambda x: x.played_at, reverse=True)
        log.info("[%s] 履歴 API から %d 局を取得", time_mode, len(games))
        return games

    @staticmethod
    def _parse_game(g: dict, time_mode: str) -> GameEntry:
        gid = str(g["id"])
        if not GAME_ID_RE.match(gid):
            raise ValueError(f"想定外の game_id: {gid!r}")
        p = [Player(str(x.get("id", "")), str(x.get("name", "")), x.get("oldR")) for x in g["players"][:2]]
        status = str(g.get("finalStatus") or "")
        return GameEntry(
            game_id=gid,
            time_mode=time_mode,
            played_at=utc_iso_to_jst(g.get("created", "")),
            handicap=HANDICAP_LABELS.get(g.get("handicap"), str(g.get("handicap"))),
            sente=p[0],
            gote=p[1],
            final_status=status,
            length=int(g.get("length") or 0),
            end_reason=end_reason_from_status(status),
        )

    # ------------------------------------------------------------ CSA
    def download_csa(self, game: GameEntry) -> str:
        """CSA を取得。まだ生成されていない（空・不正）場合は retry_wait_sec 待って 1 回だけ再取得。"""
        for attempt in (1, 2):
            text = self._get_csa(game.game_id)
            if self._looks_complete(text, game):
                return text
            if attempt == 1:
                log.info("%s: CSA 未生成/不完全 → %s 秒後に再取得", game.game_id, self.retry_wait)
                time.sleep(self.retry_wait)
        raise ValueError("CSA が取得できませんでした（未生成の可能性）")

    def _get_csa(self, game_id: str) -> str:
        resp = self._get(f"{self.api_base}/history/download/", params={"id": game_id})
        raw = resp.content
        for enc in ("utf-8-sig", "cp932"):
            try:
                return raw.decode(enc).replace("\r\n", "\n")
            except UnicodeDecodeError:
                continue
        return raw.decode("utf-8", errors="replace").replace("\r\n", "\n")

    @staticmethod
    def _looks_complete(text: str, game: GameEntry) -> bool:
        if not any(line.startswith(("N+", "P1", "PI")) for line in text.splitlines()):
            return False
        moves = count_csa_moves(text)
        # API の length は終局アクション込みのことがあるので 1 手の差は許容
        return game.length <= 1 or moves >= game.length - 1
