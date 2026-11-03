"""悪手検出の結果（data/analysis/mistakes.csv）から「次の一手」問題集の HTML を作る。

使い方:
    .venv/bin/python make_quiz.py                     # quiz/index.html を作る（全カテゴリ）
    .venv/bin/python make_quiz.py --min-category 悪手  # 悪手以上（詰み逃し・大悪手・悪手）だけ
    .venv/bin/python make_quiz.py --out /path/to/quiz.html

出力は1ファイルで完結した HTML です（外部ライブラリ・通信なし）。ブラウザで直接開いて使えます。
正解判定:
    - AI 推奨1位の手 → 正解
    - AI 推奨2・3位のうち、1位との期待勝率の差が疑問手の基準（config の thresholds.dubious）未満の手 → 正解（別解）
    - 実戦で指した手 → 不正解
    - それ以外の手は AI が読んでいないため「判定不能」として答えを表示
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import cshogi

from analysis import schema
from analysis.kifu import move_to_ja

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "analysis" / "quiz_template.html"


def parse_eval(s: str) -> tuple[float | None, str]:
    """`+350` / `#+5` / `#-3` → (自分視点の期待勝率の元になる cp 値 or ±inf, 表示用文字列)。"""
    s = (s or "").strip()
    if not s:
        return None, ""
    if s.startswith("#"):
        n = s[2:] or "?"
        if s[1] == "+":
            return math.inf, f"{n}手詰め（勝ち）"
        return -math.inf, f"{n}手で詰まされる"
    try:
        return float(int(s)), s
    except ValueError:
        return None, s


def winrate(cp: float | None, scale: float) -> float | None:
    if cp is None:
        return None
    if cp == math.inf:
        return 1.0
    if cp == -math.inf:
        return 0.0
    return 1.0 / (1.0 + math.exp(-cp / scale))


def ja_pv_to_usi(sfen: str, pv_ja: str, prev_usi: str | None) -> list[str]:
    """日本語の読み筋（空白区切り）を USI 列に戻す。合わない手が出たらそこで打ち切る。"""
    b = cshogi.Board(sfen)
    out: list[str] = []
    prev = prev_usi
    for tok in (pv_ja or "").split():
        found = None
        for m in b.legal_moves:
            u = cshogi.move_to_usi(m)
            if move_to_ja(b, u, prev) == tok:
                found = (m, u)
                break
        if not found:
            break
        b.push(found[0])
        out.append(found[1])
        prev = found[1]
    return out


def load_prev_moves(game_id: str) -> dict[int, str]:
    rows = schema.read_csv(ROOT / schema.MOVES_DIR_REL / f"{game_id}.csv")
    return {int(r["ply"]): r["move_usi"] for r in rows if r.get("ply")}


def build_problems(min_rank: int, scale: float, ok_margin: float) -> list[dict]:
    games = {r["game_id"]: r for r in schema.read_csv(ROOT / "data" / "games_summary.csv")}
    rows = schema.read_csv(ROOT / schema.MISTAKES_REL)
    prev_cache: dict[str, dict[int, str]] = {}
    problems = []
    for r in rows:
        cat = r["category"]
        if cat not in schema.CATEGORIES or schema.CATEGORIES.index(cat) > min_rank:
            continue
        sfen = r["sfen_before"]
        gid, ply = r["game_id"], int(r["ply"])
        if gid not in prev_cache:
            prev_cache[gid] = load_prev_moves(gid)
        prev = prev_cache[gid].get(ply - 1) or None

        b = cshogi.Board(sfen)
        legal = [cshogi.move_to_usi(m) for m in b.legal_moves]

        cands = []
        for i in (1, 2, 3):
            u = r.get(f"cand{i}_usi")
            if not u or any(c["usi"] == u for c in cands):
                continue
            cp, label = parse_eval(r[f"cand{i}_eval"])
            pv = ja_pv_to_usi(sfen, r[f"cand{i}_pv"], prev) or [u]
            cands.append({"usi": u, "ja": r[f"cand{i}_move"], "eval": label, "raw": r[f"cand{i}_eval"],
                          "wr": winrate(cp, scale), "pv": pv, "pv_ja": r[f"cand{i}_pv"]})
        if not cands:
            continue
        best_wr = cands[0]["wr"]
        actual = r["move_usi"]
        for i, c in enumerate(cands):
            c["ok"] = c["usi"] != actual and (
                i == 0 or (best_wr is not None and c["wr"] is not None and best_wr - c["wr"] < ok_margin))

        after_board = cshogi.Board(sfen)
        after_board.push_usi(actual)
        reply = ja_pv_to_usi(after_board.sfen(), r["reply_pv"], actual)

        g = games.get(gid, {})
        problems.append({
            "id": f"{gid}-{ply}",
            "game_id": gid,
            "played_at": r["played_at"],
            "time_mode": r["time_mode"],
            "my_turn": r["my_turn"],
            "ply": ply,
            "category": cat,
            "result": g.get("result", ""),
            "my_rating": g.get("my_rating", ""),
            "opp_rating": g.get("opponent_rating", ""),
            "sfen": sfen,
            "prev": prev,
            "legal": legal,
            "eval_before": parse_eval(r["eval_before"])[1],
            "raw_before": r["eval_before"],
            "wr_before": float(r["winrate_before"]),
            "actual": {"usi": actual, "ja": r["move_ja"], "eval": parse_eval(r["eval_after"])[1], "raw": r["eval_after"],
                       "wr": float(r["winrate_after"]), "pv": [actual] + reply,
                       "pv_ja": " ".join(x for x in [r["move_ja"], r["reply_pv"]] if x)},
            "cands": cands,
            "report": f"../{schema.report_rel(gid)}",
        })
    problems.sort(key=lambda p: (p["played_at"], p["ply"]), reverse=True)
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description="悪手検出の結果から次の一手問題集（HTML）を作る")
    ap.add_argument("--out", default=str(ROOT / "quiz" / "index.html"), help="出力先（既定: quiz/index.html）")
    ap.add_argument("--min-category", default="疑問手", choices=schema.CATEGORIES,
                    help="この重さ以上の手だけ出題する（既定: 疑問手 = すべて）")
    a = ap.parse_args()

    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8")).get("analysis", {})
    scale = float(cfg.get("winrate_scale", 600))
    ok_margin = float((cfg.get("thresholds") or {}).get("dubious", 0.05))

    problems = build_problems(schema.CATEGORIES.index(a.min_category), scale, ok_margin)
    if not problems:
        print("出題できる局面がありません（先に analyze_mistakes.py を実行してください）", file=sys.stderr)
        return 1

    data = json.dumps(problems, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = TEMPLATE.read_text(encoding="utf-8").replace("/*__PROBLEMS__*/[]", data)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"{len(problems)} 問を書き出しました: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
