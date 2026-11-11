"""序盤研究ドリル: 序盤に何度も出てきた同じ局面のうち、間違えやすい局面を探してレポートにする。

悪手検出（analyze_mistakes.py）の結果を読むだけで、エンジンは使いません。数秒で終わります。

使い方:
    .venv/bin/python analyze_opening_study.py                     # 既定の条件で作る
    .venv/bin/python analyze_opening_study.py --max-ply 30        # 30手目までの局面だけ
    .venv/bin/python analyze_opening_study.py --min-encounters 3  # 3回以上出てきた局面だけ
    .venv/bin/python analyze_opening_study.py --mode shogi5       # 持ち時間で絞り込み
    .venv/bin/python analyze_opening_study.py --sort mistake_rate # 並べ替えの基準を変える
    .venv/bin/python analyze_opening_study.py --single-blunder-cards  # 1回だけの大悪手も詳細カードにする

出力（data/analysis/study/）:
    opening_study_report.md  勉強用レポート（GitHub / VS Code のプレビューで読む）
    opening_positions.csv    局面ごとの集計（1行 = 1局面）

考え方（詳しくは docs/opening_study.md）:
    - 全対局の自分の手番の局面を CSA から復元し、SFEN の手数を除いた「盤面 + 手番 + 持ち駒」で同じ局面をまとめる
      （手順前後で同じ局面になった場合も 1 つに数える）
    - 判定カテゴリ・低下幅は、第2パスがある手は mistakes.csv、無い手は moves/{game_id}.csv の値を使う
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from analysis import board_svg, schema
from analysis.kifu import load_game

ROOT = Path(__file__).resolve().parent
STUDY_DIR_REL = f"{schema.ANALYSIS_DIR}/study"
REPORT_NAME = "opening_study_report.md"
CSV_NAME = "opening_positions.csv"

MISTAKE_CATS = set(schema.CATEGORIES)          # 詰み逃し / 大悪手 / 悪手 / 疑問手
OK_BEST, OK_FINE = "最善一致", "問題なし"
JUDGE_ORDER = [OK_BEST, OK_FINE, "疑問手", "悪手", "大悪手", "詰み逃し"]
PATTERN_HABIT = "固定化した悪手"
PATTERN_UNSTABLE = "分岐の迷い"
PATTERN_SINGLE = "単発の大悪手"
PATTERN_EN = {PATTERN_HABIT: "Habitual Mistake", PATTERN_UNSTABLE: "Unstable Branch",
              PATTERN_SINGLE: "Single Blunder"}
TURN_JA = {"SENTE": "先手番", "GOTE": "後手番"}
RESULT_JA = {"WIN": "勝", "LOSS": "負", "DRAW": "分"}

CSV_COLUMNS = [
    "rank", "pattern_type", "normalized_sfen", "sfen_before", "side", "min_ply", "avg_ply",
    "total_encounters", "mistake_count", "n_mate_miss", "n_blunder", "n_mistake", "n_dubious",
    "mistake_rate", "total_winrate_drop", "avg_mistake_drop", "avg_winrate_before",
    "distinct_moves", "top_move_ja", "top_move_usi", "top_move_count", "top_move_judge",
    "worst_move_ja", "worst_move_usi",
    "cand1_move", "cand1_usi", "cand1_eval", "cand1_pv",
    "cand2_move", "cand2_usi", "cand2_eval", "cand2_pv",
    "cand3_move", "cand3_usi", "cand3_eval", "cand3_pv",
    "played_moves", "game_ids", "model_id",
]


# ------------------------------------------------------------------ データ
@dataclass
class Encounter:
    """ある対局のある手番で、自分がその局面から指した 1 回分。"""
    game_id: str
    played_at: str
    time_mode: str
    result: str
    ply: int
    side: str
    sfen: str
    bod: str
    prev_usi: str           # 直前の相手の指し手（盤面図で強調する）
    move_usi: str
    move_ja: str
    best_usi: str           # 第1パスの最善手
    judge: str              # 最善一致 / 問題なし / 疑問手 / 悪手 / 大悪手 / 詰み逃し
    drop: float             # 期待勝率の低下（第2パス優先）
    winrate_before: float
    eval_after: str
    mistake: dict | None    # mistakes.csv の行（あれば）

    @property
    def is_mistake(self) -> bool:
        return self.judge in MISTAKE_CATS


@dataclass
class MoveSummary:
    usi: str
    ja: str
    encs: list[Encounter] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.encs)

    @property
    def mistake_count(self) -> int:
        return sum(e.is_mistake for e in self.encs)

    @property
    def judges(self) -> Counter:
        return Counter(e.judge for e in self.encs)

    @property
    def main_judge(self) -> str:
        """一番多い判定（同数なら重いほう）。"""
        c = self.judges
        return max(c, key=lambda j: (c[j], JUDGE_ORDER.index(j)))

    @property
    def avg_drop(self) -> float:
        return statistics.mean(e.drop for e in self.encs)

    @property
    def wins(self) -> int:
        return sum(e.result == "WIN" for e in self.encs)

    @property
    def losses(self) -> int:
        return sum(e.result == "LOSS" for e in self.encs)

    def reply_pv(self) -> str:
        """代表的な反撃手順（低下が最も大きかった回の reply_pv）。"""
        rows = [e for e in self.encs if e.mistake and e.mistake.get("reply_pv")]
        if not rows:
            return ""
        return max(rows, key=lambda e: e.drop).mistake["reply_pv"]


@dataclass
class Position:
    key: str
    encs: list[Encounter] = field(default_factory=list)
    pattern: str = ""

    # --- 基本の集計
    @property
    def side(self) -> str:
        return self.encs[0].side

    @property
    def n(self) -> int:
        return len(self.encs)

    @property
    def mistakes(self) -> list[Encounter]:
        return [e for e in self.encs if e.is_mistake]

    @property
    def m(self) -> int:
        return len(self.mistakes)

    @property
    def rate(self) -> float:
        return self.m / self.n

    @property
    def total_drop(self) -> float:
        # 正解した回の小さなマイナス（探索の揺れ）で打ち消し合わないよう、0 未満は 0 として足す
        return sum(max(0.0, e.drop) for e in self.encs)

    @property
    def avg_mistake_drop(self) -> float:
        return statistics.mean(e.drop for e in self.mistakes) if self.mistakes else 0.0

    @property
    def min_ply(self) -> int:
        return min(e.ply for e in self.encs)

    @property
    def avg_ply(self) -> float:
        return statistics.mean(e.ply for e in self.encs)

    @property
    def avg_wr_before(self) -> float:
        return statistics.mean(e.winrate_before for e in self.encs)

    def cat_count(self, cat: str) -> int:
        return sum(e.judge == cat for e in self.encs)

    # --- 代表値
    @property
    def rep(self) -> Encounter:
        """盤面図・SFEN に使う代表（最も早い手数で出てきた回）。"""
        return min(self.encs, key=lambda e: (e.ply, e.played_at))

    @property
    def cand_row(self) -> dict | None:
        """AI 推奨手に使う第2パスの行（一番新しい対局のもの）。"""
        rows = [e for e in self.encs if e.mistake and e.mistake.get("cand1_usi")]
        return max(rows, key=lambda e: e.played_at).mistake if rows else None

    def moves(self) -> list[MoveSummary]:
        by: dict[str, MoveSummary] = {}
        for e in self.encs:
            by.setdefault(e.move_usi, MoveSummary(e.move_usi, e.move_ja)).encs.append(e)
        # 回数の多い順。同数なら正解手を先に
        return sorted(by.values(), key=lambda s: (-s.count, s.mistake_count, s.usi))

    @property
    def top_move(self) -> MoveSummary:
        ms = self.moves()
        top = ms[0].count
        # 最多タイが複数あれば、悪手として指した回数が多いほうを「最も指した手」とする
        return max((s for s in ms if s.count == top), key=lambda s: (s.mistake_count, s.avg_drop))

    @property
    def worst_move(self) -> MoveSummary | None:
        ms = [s for s in self.moves() if s.mistake_count]
        return max(ms, key=lambda s: (s.mistake_count, s.avg_drop)) if ms else None


# ------------------------------------------------------------------ 読み込み
def normalize_sfen(sfen: str) -> str:
    """`盤面 手番 持ち駒 手数` → `盤面 手番 持ち駒`。"""
    return " ".join(sfen.split()[:3])


def load_config() -> dict:
    return json.loads((ROOT / "config.json").read_text(encoding="utf-8"))


def default_model(index: dict[str, dict]) -> str:
    """最後に解析した対局のモデル（= 現在の主モデル）。"""
    if not index:
        return ""
    return max(index.values(), key=lambda r: r.get("analyzed_at", ""))["model_id"]


def _f(s, default: float = 0.0) -> float:
    try:
        return float(s)
    except (TypeError, ValueError):
        return default


def collect_encounters(a: argparse.Namespace) -> tuple[list[Encounter], dict]:
    index = schema.load_index(ROOT)
    model = a.model or default_model(index)
    games = schema.read_csv(ROOT / "data" / "games_summary.csv")
    mistakes: dict[tuple[str, int], dict] = {}
    for r in schema.read_csv(ROOT / schema.MISTAKES_REL):
        if r.get("model_id") == model:
            mistakes[(r["game_id"], int(r["ply"]))] = r

    stats = Counter()
    encs: list[Encounter] = []
    for g in games:
        gid = g["game_id"]
        idx = index.get(gid)
        if not idx:
            stats["未解析"] += 1
            continue
        if idx.get("model_id") != model:
            stats["別モデル"] += 1
            continue
        if g.get("handicap") != a.handicap:
            stats["手合い違い"] += 1
            continue
        if a.mode and g.get("time_mode") not in a.mode:
            stats["持ち時間違い"] += 1
            continue
        if idx.get("csa_hash") and g.get("csa_hash") and idx["csa_hash"] != g["csa_hash"]:
            stats["棋譜更新後に未解析"] += 1
            continue
        moves = schema.read_csv(ROOT / schema.MOVES_DIR_REL / f"{gid}.csv")
        if not moves:
            stats["moves なし"] += 1
            continue
        game = load_game(ROOT / g["csa_rel_path"])
        stats["対象"] += 1

        wr_after = {int(r["ply"]): _f(r["winrate"], 0.5) for r in moves}
        for r in moves:
            if r.get("is_my_move") != "1":
                continue
            ply = int(r["ply"])
            if ply > a.max_ply:
                continue
            k = ply - 1
            if k >= game.n or game.moves[k] != r["move_usi"]:
                raise SystemExit(f"{gid} {ply}手目: CSA と moves CSV の指し手が一致しません（再解析が必要です）")
            mrow = mistakes.get((gid, ply))
            cat = (mrow or {}).get("category") or r.get("category") or ""
            if cat in MISTAKE_CATS:
                judge = cat
            elif r["move_usi"] == r.get("best_usi"):
                judge = OK_BEST
            else:
                judge = OK_FINE
            encs.append(Encounter(
                game_id=gid, played_at=g["played_at"], time_mode=g["time_mode"], result=g.get("result", ""),
                ply=ply, side=game.turns[k], sfen=game.sfens[k], bod=game.bods[k],
                prev_usi=game.moves[k - 1] if k > 0 else "",
                move_usi=r["move_usi"], move_ja=r["move_ja"], best_usi=r.get("best_usi", ""),
                judge=judge,
                drop=_f(mrow["winrate_drop"]) if mrow else _f(r.get("winrate_drop")),
                winrate_before=_f(mrow["winrate_before"]) if mrow else wr_after.get(ply - 1, 0.5),
                eval_after=(mrow or {}).get("eval_after") or r.get("eval", ""),
                mistake=mrow,
            ))
    return encs, {"model": model, "stats": stats,
                  "model_name": next((r["model_name"] for r in index.values() if r["model_id"] == model), model)}


# ------------------------------------------------------------------ 抽出・分類
def classify(pos: Position, a: argparse.Namespace) -> str:
    if pos.n == 1:
        return PATTERN_SINGLE
    top = pos.top_move
    if pos.rate >= a.habit_rate and top.main_judge in MISTAKE_CATS:
        return PATTERN_HABIT
    return PATTERN_UNSTABLE


SORT_KEYS = {
    "total_drop": lambda p: (-p.total_drop, -p.m, p.min_ply),
    "mistake_rate": lambda p: (-p.rate, -p.total_drop, p.min_ply),
    "encounters": lambda p: (-p.n, -p.total_drop, p.min_ply),
    "ply": lambda p: (p.min_ply, -p.total_drop),
}


def extract(encs: list[Encounter], a: argparse.Namespace) -> tuple[list[Position], list[Position], Counter]:
    by: dict[str, Position] = {}
    for e in encs:
        by.setdefault(normalize_sfen(e.sfen), Position(normalize_sfen(e.sfen))).encs.append(e)

    lo, hi = a.decided_low, a.decided_high
    main, single, why = [], [], Counter()
    for p in by.values():
        if not p.m:
            continue
        why["疑問手以上を指した局面"] += 1
        if not (lo <= p.avg_wr_before <= hi):
            why["大勢判明で除外"] += 1
            continue
        if p.n >= a.min_encounters and p.m >= a.min_mistakes:
            p.pattern = classify(p, a)
            main.append(p)
        elif p.n == 1 and p.mistakes[0].drop >= a.single_blunder_drop:
            p.pattern = PATTERN_SINGLE
            single.append(p)
        else:
            why["遭遇回数・悪手回数が基準未満"] += 1
    key = SORT_KEYS[a.sort]
    main.sort(key=key)
    single.sort(key=key)
    return main, single, why


# ------------------------------------------------------------------ 出力: CSV
def _cands(row: dict | None) -> list[tuple[str, str, str, str]]:
    if not row:
        return []
    out = []
    for i in (1, 2, 3):
        if row.get(f"cand{i}_usi"):
            out.append((row[f"cand{i}_move"], row[f"cand{i}_usi"], row[f"cand{i}_eval"], row[f"cand{i}_pv"]))
    return out


def _played_moves_str(p: Position) -> str:
    parts = []
    for s in p.moves():
        j = "/".join(f"{k}{v}" for k, v in sorted(s.judges.items(), key=lambda kv: JUDGE_ORDER.index(kv[0])))
        parts.append(f"{s.ja}×{s.count}[{j}]")
    return " ; ".join(parts)


def csv_rows(positions: list[Position], model: str) -> list[dict]:
    rows = []
    for rank, p in enumerate(positions, 1):
        top, worst, rep = p.top_move, p.worst_move, p.rep
        r = {
            "rank": rank, "pattern_type": p.pattern, "normalized_sfen": p.key, "sfen_before": rep.sfen,
            "side": p.side, "min_ply": p.min_ply, "avg_ply": f"{p.avg_ply:.1f}",
            "total_encounters": p.n, "mistake_count": p.m,
            "n_mate_miss": p.cat_count("詰み逃し"), "n_blunder": p.cat_count("大悪手"),
            "n_mistake": p.cat_count("悪手"), "n_dubious": p.cat_count("疑問手"),
            "mistake_rate": f"{p.rate:.3f}", "total_winrate_drop": f"{p.total_drop:.4f}",
            "avg_mistake_drop": f"{p.avg_mistake_drop:.4f}", "avg_winrate_before": f"{p.avg_wr_before:.4f}",
            "distinct_moves": len(p.moves()),
            "top_move_ja": top.ja, "top_move_usi": top.usi, "top_move_count": top.count,
            "top_move_judge": top.main_judge,
            "worst_move_ja": worst.ja if worst else "", "worst_move_usi": worst.usi if worst else "",
            "played_moves": _played_moves_str(p),
            "game_ids": " ".join(sorted({e.game_id for e in p.encs})),
            "model_id": model,
        }
        for i, (ja, usi, ev, pv) in enumerate(_cands(p.cand_row), 1):
            r.update({f"cand{i}_move": ja, f"cand{i}_usi": usi, f"cand{i}_eval": ev, f"cand{i}_pv": pv})
        rows.append(r)
    return rows


# ------------------------------------------------------------------ 出力: Markdown
def _md(v) -> str:
    return str(v if v not in (None, "") else "-").replace("|", "\\|").replace("\n", " ")


def _pt(x: float) -> str:
    return f"{-x * 100:+.1f}pt"


def _pct(x: float) -> str:
    return f"{x * 100:.0f}%"


def _report_link(gid: str) -> str:
    return f"[{gid}](../reports/{gid}.md)"


def _judge_str(s: MoveSummary) -> str:
    c = s.judges
    parts = []
    for j in JUDGE_ORDER:
        if c[j]:
            label = f"**{j}**" if j in MISTAKE_CATS else j
            parts.append(label if s.count == 1 else f"{label}×{c[j]}")
    return " / ".join(parts)


def _eval_str(s: MoveSummary) -> str:
    vals = [e.eval_after for e in s.encs if e.eval_after]
    cps = [int(v) for v in vals if not v.startswith("#")]
    if len(cps) == len(vals) and cps:
        return f"{round(statistics.mean(cps)):+d}"
    return " / ".join(dict.fromkeys(vals)) or "-"


def _heading(rank: int, p: Position) -> str:
    return (f"### #{rank} [{p.pattern}] {TURN_JA.get(p.side, p.side)} {p.min_ply}手目付近"
            f"（遭遇: {p.n}回 / 疑問手以上: {p.m}回 / 累計勝率低下: {_pt(p.total_drop)}）")


def _anchor(prefix: str, rank: int) -> str:
    return f'<a id="{prefix}-{rank}"></a>'


def board_block(rank: int, p: Position, prefix: str, images: dict[str, str]) -> list[str]:
    """代表局面の盤面画像（赤＝一番多く間違えた手、青＝AI 推奨1位）と折りたたんだ BOD。"""
    rep = p.rep
    worst = p.worst_move
    cands = _cands(p.cand_row)
    best_usi = cands[0][1] if cands else (rep.best_usi or None)
    best_ja = cands[0][0] if cands else None
    rel = f"img/{prefix}_{rank:02d}.svg"
    images[rel] = board_svg.position_svg(rep.sfen, rep.ply, played=worst.usi if worst else None, best=best_usi,
                                         last=rep.prev_usi or None, my_turn=rep.side)
    return board_svg.markdown_block(rel, f"#{rank} の局面", rep.bod, worst.ja if worst else None, best_ja)


def card(rank: int, p: Position, prefix: str, images: dict[str, str]) -> list[str]:
    """詳細カード。盤面画像は images {出力先からの相対パス: SVG} に追加する。"""
    rep = p.rep
    cands = _cands(p.cand_row)
    cand_rank = {usi: i for i, (_ja, usi, _ev, _pv) in enumerate(cands, 1)}
    L = [_anchor(prefix, rank), _heading(rank, p), ""]
    plies = sorted({e.ply for e in p.encs})
    ply_note = f"{plies[0]}手目" if len(plies) == 1 else f"{plies[0]}〜{plies[-1]}手目（手順前後で合流）"
    L += [
        f"- パターン: **{p.pattern}**（{PATTERN_EN[p.pattern]}）　疑問手以上率 {_pct(p.rate)}"
        f"（{p.m}/{p.n}）、平均勝率低下（間違えた回）{_pt(p.avg_mistake_drop)}",
        f"- 出現: {ply_note}、着手前の期待勝率 平均 {_pct(p.avg_wr_before)}",
        "",
        *board_block(rank, p, prefix, images),
        "",
        f"SFEN: `{rep.sfen}`",
        "",
        "**実戦での指し手比較**",
        "",
        "| 自分の指し手 | 回数 | 判定 | AI順位 | 平均勝率低下 | 着手後評価値 | 実戦勝敗 | 主な反撃手順 (`reply_pv`) |",
        "|---|--:|---|:-:|--:|--:|---|---|",
    ]
    for s in p.moves():
        cr = cand_rank.get(s.usi)
        ai = f"{cr}位" if cr else ("1位※" if any(e.best_usi == s.usi for e in s.encs) else "-")
        wl = f"{s.wins}勝{s.losses}敗"
        L.append(f"| {s.ja} | {s.count} | {_judge_str(s)} | {ai} | {_pt(s.avg_drop)} | {_eval_str(s)} "
                 f"| {wl} | {_md(s.reply_pv())} |")
    L += ["", "AI順位: 第2パス（MultiPV）の候補順位。「1位※」は第1パスの最善手と一致（第2パスでは読んでいない）。", ""]

    L += ["**AI 推奨の定跡（第2パス MultiPV）**", ""]
    if cands:
        src = p.cand_row
        for i, (ja, _usi, ev, pv) in enumerate(cands, 1):
            L.append(f"- 推奨{i}位: **{ja}**（{ev}）　読み筋: {_md(pv)}")
        L += ["", f"（{src['game_id']} の {src['ply']}手目の解析結果。対局ごとに数値が少し揺れることがあります）"]
    else:
        L.append("- 第2パスの候補手がありません")
    L += ["", "**該当対局**", "", "| 対局 | 日時 | 持ち時間 | 手数 | 指し手 | 判定 | 勝敗 |", "|---|---|---|--:|---|---|---|"]
    for e in sorted(p.encs, key=lambda e: (not e.is_mistake, e.played_at), reverse=False):
        j = f"**{e.judge}**" if e.is_mistake else e.judge
        L.append(f"| {_report_link(e.game_id)} | {e.played_at} | {e.time_mode} | {e.ply} | {e.move_ja} | {j} "
                 f"| {RESULT_JA.get(e.result, e.result)} |")
    L += ["", "[▲ 早見表に戻る](#早見表)", ""]
    return L


def summary_table(positions: list[Position], prefix: str, limit: int | None) -> list[str]:
    L = ["| 順位 | 手番 | 手数目安 | パターン | 遭遇 | 悪手率 | 累計勝率損失 | 最も指した悪手 | AI 最善手 |",
         "|--:|---|--:|---|--:|--:|--:|---|---|"]
    for rank, p in enumerate(positions[:limit] if limit else positions, 1):
        worst = p.worst_move
        cr = p.cand_row
        L.append(f"| [{rank}](#{prefix}-{rank}) | {TURN_JA.get(p.side, p.side)} | {p.min_ply} | {p.pattern} | {p.n} "
                 f"| {_pct(p.rate)} | {_pt(p.total_drop)} | {worst.ja if worst else '-'} "
                 f"| {cr['cand1_move'] if cr else '-'} |")
    return L


def markdown(main: list[Position], single: list[Position], encs: list[Encounter], meta: dict,
             why: Counter, a: argparse.Namespace, images: dict[str, str]) -> str:
    """レポート本文を返す。盤面画像は images に追加する（呼び出し側で書き出す）。"""
    n_games = len({e.game_id for e in encs})
    n_pos = len({normalize_sfen(e.sfen) for e in encs})
    n_repeat = sum(1 for c in Counter(normalize_sfen(e.sfen) for e in encs).values() if c >= a.min_encounters)
    pc = Counter(p.pattern for p in main)
    mode = "・".join(a.mode) if a.mode else "すべて"
    L = [
        "# 序盤研究ドリル（頻出局面の悪手・疑問手）",
        "",
        "[README に戻る](../../../README.md)　/　見方: [docs/opening_study.md](../../../docs/opening_study.md)"
        "　/　データ: [opening_positions.csv](opening_positions.csv)",
        "",
        "`analyze_opening_study.py` が自動生成。序盤に何度も出てきた同じ局面（手順前後で合流した局面を含む）のうち、"
        "疑問手以上を指したことがある局面を、累計の期待勝率損失が大きい順に並べています。",
        "",
        "## サマリー",
        "",
        "| 項目 | 内容 |",
        "|---|---|",
        f"| 評価関数 | {meta['model_name']}（`{meta['model']}`） |",
        f"| 対象 | 手合い {a.handicap} / 持ち時間 {mode} / **{n_games} 局** |",
        f"| 対象手数 | 1〜{a.max_ply}手目の自分の手（{len(encs)} 手、異なる局面 {n_pos}、{a.min_encounters} 回以上出てきた局面 {n_repeat}） |",
        f"| 抽出条件 | 遭遇 {a.min_encounters} 回以上・疑問手以上 {a.min_mistakes} 回以上・着手前の期待勝率の平均が "
        f"{_pct(a.decided_low)}〜{_pct(a.decided_high)} |",
        f"| 問題局面 | **{len(main)} 件**（{PATTERN_HABIT} {pc[PATTERN_HABIT]} 件 / {PATTERN_UNSTABLE} {pc[PATTERN_UNSTABLE]} 件） |",
        f"| 別枠: {PATTERN_SINGLE} | {len(single)} 件（1回だけ出てきた局面で勝率 {a.single_blunder_drop * 100:.0f}pt 以上の低下） |",
        f"| 並べ替え | `{a.sort}` |",
        "",
        "パターンの意味:",
        "",
        f"- **{PATTERN_HABIT}**: 疑問手以上率 {_pct(a.habit_rate)} 以上で、いちばん多く指している手が疑問手以上。"
        "定跡の誤暗記や手癖の可能性 → AI 推奨手で上書きする",
        f"- **{PATTERN_UNSTABLE}**: 正しく指せた回もあるが、ときどき間違える（または指し手が割れている）。"
        "反撃手順（`reply_pv`）を見て、なぜその手が悪いのかを理解する",
        "",
        "## 早見表",
        "",
    ]
    if main:
        L += summary_table(main, "pos", a.top)
        if len(main) > a.top:
            L += ["", f"（上位 {a.top} 件。全 {len(main)} 件は下の詳細カードと CSV を参照）"]
    else:
        L.append("条件に合う局面はありませんでした。対局が増えるか、`--min-encounters` / `--max-ply` を変えると見つかることがあります。")
    L += ["", "## 局面別の詳細カード", ""]
    for rank, p in enumerate(main, 1):
        L += card(rank, p, "pos", images)

    L += [f"## 別枠: {PATTERN_SINGLE}（1回だけ出てきた局面）", ""]
    if single:
        L += ["まだ1回しか出てきていない局面ですが、序盤で大きく損をした手です。同じ局面がまた出てきたら上のリストに入ります。", ""]
        if a.single_blunder_cards:
            L += summary_table(single, "single", None)
            L.append("")
            for rank, p in enumerate(single, 1):
                L += card(rank, p, "single", images)
        else:
            L += ["対局 ID のリンクから対局別レポートの該当手番に飛べます。詳細カードは `--single-blunder-cards` で出力します。", ""]
            L += ["| 順位 | 対局 | 手数 | 指し手 | 判定 | 勝率低下 | AI 最善手 |", "|--:|---|--:|---|---|--:|---|"]
            for rank, p in enumerate(single, 1):
                e = p.encs[0]
                L.append(f"| {rank} | [{e.game_id}](../reports/{e.game_id}.md#ply-{e.ply}) | {e.ply} | {e.move_ja} "
                         f"| {e.judge} | {_pt(e.drop)} | {(e.mistake or {}).get('cand1_move') or '-'} |")
            L.append("")
    else:
        L += ["該当なし。", ""]

    L += ["## 集計の内訳", "", "| 項目 | 件数 |", "|---|--:|"]
    for k, v in meta["stats"].items():
        L.append(f"| 対局: {k} | {v} |")
    for k, v in why.items():
        L.append(f"| 局面: {k} | {v} |")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ CLI
def main() -> int:
    ap = argparse.ArgumentParser(description="序盤の頻出局面から、間違えやすい局面を探して研究用レポートを作る")
    ap.add_argument("--max-ply", type=int, default=50, help="この手数までの局面を対象にする（既定: 50）")
    ap.add_argument("--min-encounters", type=int, default=2, help="同じ局面に遭遇した回数の下限（既定: 2）")
    ap.add_argument("--min-mistakes", type=int, default=1, help="疑問手以上を指した回数の下限（既定: 1）")
    ap.add_argument("--model", default="", help="評価関数の ID（既定: 最後に解析した対局のモデル）")
    ap.add_argument("--handicap", default="平手", help="手合い（既定: 平手）")
    ap.add_argument("--mode", action="append", choices=["shogi10", "shogi5", "shogi2"],
                    help="持ち時間で絞り込み（複数指定可。既定: すべて）")
    ap.add_argument("--decided-low", type=float, default=0.15,
                    help="着手前の期待勝率の平均がこれ未満の局面は除外（既定: 0.15）")
    ap.add_argument("--decided-high", type=float, default=0.85,
                    help="着手前の期待勝率の平均がこれを超える局面は除外（既定: 0.85）")
    ap.add_argument("--habit-rate", type=float, default=0.6,
                    help=f"「{PATTERN_HABIT}」と判定する疑問手以上率の下限（既定: 0.6）")
    ap.add_argument("--single-blunder-drop", type=float, default=None,
                    help="別枠「単発の大悪手」の勝率低下の下限（既定: config の thresholds.blunder = 0.20）")
    ap.add_argument("--single-blunder-cards", action="store_true", help="単発の大悪手も詳細カードで出力する")
    ap.add_argument("--sort", choices=list(SORT_KEYS), default="total_drop",
                    help="並べ替え（既定: total_drop = 累計の勝率損失が大きい順）")
    ap.add_argument("--top", type=int, default=10, help="早見表に載せる件数（既定: 10）")
    ap.add_argument("--out-dir", default=str(ROOT / STUDY_DIR_REL), help=f"出力先（既定: {STUDY_DIR_REL}）")
    a = ap.parse_args()
    if a.single_blunder_drop is None:
        th = load_config().get("analysis", {}).get("thresholds") or {}
        a.single_blunder_drop = float(th.get("blunder", 0.20))

    encs, meta = collect_encounters(a)
    if not encs:
        print("対象の手がありません（先に analyze_mistakes.py を実行してください）", file=sys.stderr)
        return 1
    main_pos, single_pos, why = extract(encs, a)

    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    schema.write_csv(out / CSV_NAME, CSV_COLUMNS, csv_rows(main_pos, meta["model"]) + csv_rows(single_pos, meta["model"]))
    images: dict[str, str] = {}
    (out / REPORT_NAME).write_text(markdown(main_pos, single_pos, encs, meta, why, a, images), encoding="utf-8")
    board_svg.write_images(out, images, stale_glob="img/*.svg")

    pc = Counter(p.pattern for p in main_pos)
    print(f"対象 {meta['stats']['対象']} 局 / 1〜{a.max_ply}手目の自分の手 {len(encs)} 手")
    print(f"問題局面 {len(main_pos)} 件（{PATTERN_HABIT} {pc[PATTERN_HABIT]} / {PATTERN_UNSTABLE} {pc[PATTERN_UNSTABLE]}）"
          f"、別枠 {PATTERN_SINGLE} {len(single_pos)} 件")
    print(f"書き出し: {out / REPORT_NAME}")
    print(f"          {out / CSV_NAME}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
