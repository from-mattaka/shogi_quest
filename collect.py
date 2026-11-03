"""エントリーポイント: 履歴取得 → 未取得 CSA ダウンロード → CSV 追記 → README / docs/ai/AI_CONTEXT.md 生成。

使い方:
    python collect.py                          # config.json の設定で実行
    SHOGI_QUEST_PLAYER=xxx python collect.py   # ユーザー名を環境変数で上書き
"""
from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

from anonymize import anonymize_csa, anonymize_row
from fetcher import GameEntry, QuestFetcher, count_csa_moves
from storage import Storage, now_jst_iso

ROOT = Path(__file__).resolve().parent
log = logging.getLogger("collect")


def load_config() -> dict:
    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    cfg["player_name"] = (os.environ.get("SHOGI_QUEST_PLAYER") or cfg["player_name"]).strip()
    return cfg


def build_record(g: GameEntry, user_id: str, csa_text: str, rel_path: str, csa_hash: str) -> dict:
    me = user_id.lower()
    if g.sente.id.lower() == me:
        my_turn, mine, opp = "SENTE", g.sente, g.gote
    elif g.gote.id.lower() == me:
        my_turn, mine, opp = "GOTE", g.gote, g.sente
    else:
        my_turn, mine, opp = "", None, None
        log.warning("%s: 自分(%s)が対局者に見つかりません", g.game_id, user_id)  # 相手名はログにも出さない

    winner = g.winner()
    if winner == "DRAW":
        result = "DRAW"
    elif winner and my_turn:
        result = "WIN" if winner == my_turn else "LOSS"
    else:
        result = ""
        log.warning("%s: 勝敗を判定できません (finalStatus=%s)", g.game_id, g.final_status)

    return anonymize_row({
        "game_id": g.game_id,
        "time_mode": g.time_mode,
        "played_at": g.played_at,
        "handicap": g.handicap,
        "sente_name": g.sente.name,
        "sente_rating": g.sente.rating,
        "gote_name": g.gote.name,
        "gote_rating": g.gote.rating,
        "my_turn": my_turn,
        "my_rating": mine.rating if mine else None,
        "opponent_name": opp.name if opp else "",
        "opponent_rating": opp.rating if opp else None,
        "result": result,
        "moves_count": count_csa_moves(csa_text),
        "end_reason": g.end_reason,
        "csa_rel_path": rel_path,
        "csa_hash": csa_hash,
        "fetched_at": now_jst_iso(),
    }, user_id)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    cfg = load_config()
    user_id = cfg["player_name"]
    if not user_id or user_id == "YOUR_QUEST_NAME":
        log.error("config.json の player_name（将棋クエストのユーザー名）を設定してください")
        return 2

    store = Storage(ROOT, cfg.get("data_dir", "data"))
    fetcher = QuestFetcher(cfg)
    budget = cfg.get("max_csa_per_run", 300)
    modes: dict[str, str] = cfg["time_modes"]  # time_mode → サイトの gtype
    added = failed_modes = 0

    for mode, gtype in modes.items():
        try:
            games = fetcher.fetch_history(user_id, mode, gtype)
        except Exception as e:  # noqa: BLE001
            log.error("[%s] 履歴取得に失敗: %s", mode, e)
            failed_modes += 1
            continue

        new_games = [g for g in games if not store.exists(g.game_id)]
        log.info("[%s] 新規 %d 局", mode, len(new_games))
        if len(games) >= 30 and len(new_games) == len(games) and not store.is_first_run:
            log.warning("[%s] 取得した30局がすべて新規です。前回からの間に30局を超えて指した場合、取りこぼしがあります", mode)

        for g in reversed(new_games):  # 古い順に処理
            if budget <= 0:
                log.info("max_csa_per_run に到達。残りは次回実行で取得します")
                break
            budget -= 1  # 待機は fetcher 側で全リクエストに一律適用
            try:
                text = fetcher.download_csa(g)
            except Exception as e:  # noqa: BLE001
                log.warning("%s: CSA 取得失敗 (%s) — 次回再試行", g.game_id, e)
                continue
            text = anonymize_csa(text, user_id)  # 公開リポジトリに相手のユーザー名を残さない
            rel, digest = store.save_csa(mode, g.game_id, text)
            if store.add(build_record(g, user_id, text, rel, digest)):
                added += 1

    if added or store.is_first_run:
        store.save()
        log.info("新規 %d 局を追加しました", added)
    else:
        log.info("新規対局なし")
    # README / AI_CONTEXT は毎回作り直す（ローカルで追加された AI 解析結果も反映される）。
    # 中身はデータだけで決まるので、変化が無ければ差分も出ずコミットされない。
    store.write_readme(user_id, cfg.get("recent_games_in_readme", 20), cfg.get("quiz_url"))
    store.write_ai_context(user_id)

    return 1 if failed_modes == len(modes) else 0


if __name__ == "__main__":
    sys.exit(main())
