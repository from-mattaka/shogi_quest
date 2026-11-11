"""解析結果を CSV 行・Markdown レポートに変換する。"""
from __future__ import annotations

from . import board_svg
from .env import EngineInfo
from .evaluator import winrate_drop
from .kifu import Game
from .runner import GameAnalysis, Params, summary_counts
from .schema import CATEGORIES

TIME_MODE_LABELS = {"shogi10": "10分", "shogi5": "5分", "shogi2": "2分"}
RESULT_JA = {"WIN": "勝ち", "LOSS": "負け", "DRAW": "引き分け"}
TURN_JA = {"SENTE": "先手（▲）", "GOTE": "後手（△）"}


def _pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def _md(v) -> str:
    return str(v if v not in (None, "") else "-").replace("|", "\\|").replace("\n", " ")


def move_rows(game: Game, ga: GameAnalysis, p: Params, info: EngineInfo) -> list[dict]:
    cat = {m.ply: m.category for m in ga.mistakes}
    rows = [{"ply": 0, "eval": ga.evals[0].fmt(), "winrate": f"{ga.evals[0].winrate(p.scale):.4f}",
             "model_id": info.model_id}]
    for ply in range(1, game.n + 1):
        k = ply - 1
        mine = game.turns[k] == ga.my_turn
        b = ga.best[k]
        rows.append({
            "ply": ply,
            "mover": game.turns[k],
            "is_my_move": 1 if mine else 0,
            "move_usi": game.moves[k],
            "move_ja": game.moves_ja[k],
            "best_usi": b or "",
            "best_ja": game.move_ja_at(k, b) if b else "",
            "eval": ga.evals[ply].fmt(),
            "winrate": f"{ga.evals[ply].winrate(p.scale):.4f}",
            "winrate_drop": f"{winrate_drop(ga.evals[k], ga.evals[ply], p.scale):.4f}" if mine else "",
            "category": cat.get(ply, ""),
            "model_id": info.model_id,
        })
    return rows


def mistake_rows(meta: dict, ga: GameAnalysis, p: Params, info: EngineInfo) -> list[dict]:
    out = []
    for m in ga.mistakes:
        r = {
            "game_id": meta["game_id"], "played_at": meta["played_at"], "time_mode": meta["time_mode"],
            "my_turn": ga.my_turn, "ply": m.ply, "category": m.category,
            "winrate_before": f"{m.before.winrate(p.scale):.4f}",
            "winrate_after": f"{m.after.winrate(p.scale):.4f}",
            "winrate_drop": f"{winrate_drop(m.before, m.after, p.scale):.4f}",
            "eval_before": m.before.fmt(), "eval_after": m.after.fmt(),
            "move_usi": m.move_usi, "move_ja": m.move_ja, "reply_pv": m.reply_pv_ja,
            "sfen_before": m.sfen_before, "model_id": info.model_id, "nn_bin_sha12": info.nn_bin_sha256[:12],
        }
        for i, (usi, ja, sc, pv) in enumerate(m.candidates[:3], 1):
            r.update({f"cand{i}_move": ja, f"cand{i}_usi": usi, f"cand{i}_eval": sc.fmt(), f"cand{i}_pv": pv})
        out.append(r)
    return out


def index_row(meta: dict, game: Game, ga: GameAnalysis, p: Params, info: EngineInfo, analyzed_at: str) -> dict:
    return {
        "game_id": meta["game_id"], "csa_hash": meta["csa_hash"], "analysis_version": p.analysis_version,
        "engine_name": info.engine_name, "engine_tag": info.engine_tag,
        "model_id": info.model_id, "model_name": info.model_name, "nn_bin_sha256": info.nn_bin_sha256,
        "pass1_limit": p.pass1_limit, "pass2_limit": p.pass2_limit, "pass2_multipv": p.pass2_multipv,
        "threads": p.threads, "hash_mb": p.hash_mb,
        "my_moves": len(ga.my_plies(game)), "n_candidates": len(ga.candidates),
        **summary_counts(ga),
        "elapsed_sec": f"{ga.elapsed:.1f}", "analyzed_at": analyzed_at,
    }


def _chart(game: Game, ga: GameAnalysis, p: Params) -> list[str]:
    vals = ", ".join(f"{e.winrate(p.scale) * 100:.1f}" for e in ga.evals)
    half = ", ".join("50" for _ in ga.evals)
    return [
        "```mermaid",
        "xychart-beta",
        '    title "期待勝率の推移（自分視点, %）"',
        f'    x-axis "手数" 0 --> {game.n}',
        '    y-axis "勝率 (%)" 0 --> 100',
        f"    line [{vals}]",
        f"    line [{half}]",
        "```",
    ]


def board_image_rel(game_id: str, ply: int) -> str:
    """レポート（reports/{game_id}.md）から見た盤面画像の相対パス。"""
    return f"img/{game_id}_{ply:03d}.svg"


def board_images(game_id: str, game: Game, ga: GameAnalysis) -> dict[str, str]:
    """課題局面ごとの盤面画像 {reports からの相対パス: SVG}。"""
    out = {}
    for m in ga.mistakes:
        k = m.ply - 1
        out[board_image_rel(game_id, m.ply)] = board_svg.position_svg(
            m.sfen_before, m.ply, played=m.move_usi, best=m.candidates[0][0] if m.candidates else None,
            last=game.moves[k - 1] if k > 0 else None, my_turn=ga.my_turn)
    return out


def markdown(meta: dict, game: Game, ga: GameAnalysis, p: Params, info: EngineInfo, analyzed_at: str) -> str:
    gid = meta["game_id"]
    up = "../../../"
    opp = meta["opponent_name"] + (f"（{meta['opponent_rating']}）" if meta.get("opponent_rating") else "")
    counts = {c: sum(1 for m in ga.mistakes if m.category == c) for c in CATEGORIES}
    L = [
        f"# 解析レポート {gid}",
        "",
        f"[README に戻る]({up}README.md)　/　棋譜: [CSA]({up}{meta['csa_rel_path']})　/　"
        f"解析の見方: [docs/mistake_analysis.md]({up}docs/mistake_analysis.md)",
        "",
        "## 対局情報",
        "",
        "| 項目 | 内容 |",
        "|---|---|",
        f"| 日時 | {meta['played_at']} |",
        f"| 持ち時間 | {TIME_MODE_LABELS.get(meta['time_mode'], meta['time_mode'])} |",
        f"| 自分 | {TURN_JA.get(ga.my_turn, ga.my_turn)}（{_md(meta.get('my_rating'))}） |",
        f"| 相手 | {_md(opp)} |",
        f"| 結果 | {RESULT_JA.get(meta['result'], meta['result'])}（{meta['end_reason']}, {game.n}手） |",
        "",
        "## 解析環境",
        "",
        "| 項目 | 内容 |",
        "|---|---|",
        f"| エンジン | {_md(info.engine_name)}（{info.engine_tag}） |",
        f"| 評価関数 | **{info.model_name}**（`{info.model_id}`） |",
        f"| nn.bin SHA-256 | `{info.nn_bin_sha256}` |",
        f"| 第1パス | {p.pass1_limit}, MultiPV 1 |",
        f"| 第2パス | {p.pass2_limit}, MultiPV {p.pass2_multipv} |",
        f"| Threads / Hash | {p.threads} / {p.hash_mb}MB |",
        f"| 判定基準 | 疑問手 ≥{p.thresholds.dubious * 100:.0f}pt, 悪手 ≥{p.thresholds.mistake * 100:.0f}pt, "
        f"大悪手 ≥{p.thresholds.blunder * 100:.0f}pt（期待勝率 W(E)=1/(1+exp(-E/{p.scale:g}))） |",
        f"| 解析日時 | {analyzed_at}（解析バージョン {p.analysis_version}, {ga.elapsed:.0f}秒） |",
        "",
        "## サマリー",
        "",
        "| 自分の手数 | 深掘りした手 | " + " | ".join(CATEGORIES) + " |",
        "|--:|--:|" + "--:|" * len(CATEGORIES),
        f"| {len(ga.my_plies(game))} | {len(ga.candidates)} | " + " | ".join(str(counts[c]) for c in CATEGORIES) + " |",
        "",
        "## 期待勝率の推移",
        "",
        *_chart(game, ga, p),
        "",
        "<details><summary>1手ごとの数値（第1パス）</summary>",
        "",
        "| 手数 | 指し手 | 評価値 | 勝率 | 低下 | 判定 |",
        "|--:|---|--:|--:|--:|---|",
    ]
    cat = {m.ply: m.category for m in ga.mistakes}
    for ply in range(1, game.n + 1):
        k = ply - 1
        mine = game.turns[k] == ga.my_turn
        drop = f"{winrate_drop(ga.evals[k], ga.evals[ply], p.scale) * 100:+.1f}pt" if mine else ""
        mark = cat.get(ply, "")
        if mark:
            mark = f"[{mark}](#ply-{ply})"
        L.append(f"| {ply} | {game.moves_ja[k]} | {ga.evals[ply].fmt()} | {_pct(ga.evals[ply].winrate(p.scale))} "
                 f"| {drop} | {mark} |")
    L += ["", "</details>", "", "## 課題局面", ""]
    if not ga.mistakes:
        L.append("判定基準に該当する手はありませんでした。")
    for m in ga.mistakes:
        drop = winrate_drop(m.before, m.after, p.scale)
        L += [
            f'<a id="ply-{m.ply}"></a>',
            f"### {m.ply}手目 {m.move_ja} — {m.category}",
            "",
            "| | 着手前 | 着手後 | 差 |",
            "|---|--:|--:|--:|",
            f"| 期待勝率 | {_pct(m.before.winrate(p.scale))} | {_pct(m.after.winrate(p.scale))} | {-drop * 100:+.1f}pt |",
            f"| 評価値 | {m.before.fmt_ja()} | {m.after.fmt_ja()} | |",
            "",
            "着手前の局面:",
            "",
            *board_svg.markdown_block(board_image_rel(gid, m.ply), f"{m.ply}手目の局面", m.bod_before,
                                      m.move_ja, m.candidates[0][1] if m.candidates else None),
            "",
            "| | 指し手 | 評価値 | 読み筋 |",
            "|---|---|--:|---|",
            f"| 実戦 | {m.move_ja} | {m.after.fmt_ja()} | {_md(m.reply_pv_ja)} |",
        ]
        for i, (_usi, ja, sc, pv) in enumerate(m.candidates, 1):
            L.append(f"| AI {i}位 | {ja} | {sc.fmt_ja()} | {_md(pv)} |")
        L += ["", f"SFEN: `{m.sfen_before}`", ""]
    return "\n".join(L) + "\n"
