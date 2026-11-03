"""将棋AI（やねうら王＋評価関数）による棋譜解析。ローカルで手動実行する。

使い方（詳しくは docs/mistake_analysis.md）:
    .venv/bin/python analyze_mistakes.py                       # 未解析の対局をすべて解析（新しい順）
    .venv/bin/python analyze_mistakes.py --limit 5             # 5局だけ
    .venv/bin/python analyze_mistakes.py --game ID [--game ID] # 対局を指定
    .venv/bin/python analyze_mistakes.py --since 2026-11-01 --mode shogi5
    .venv/bin/python analyze_mistakes.py --dry-run             # 対象の一覧だけ表示
    .venv/bin/python analyze_mistakes.py --force               # 解析済みも含めて再解析
    .venv/bin/python analyze_mistakes.py --reanalyze-model-mismatch  # 現在と違うモデルで解析した対局を再解析
    .venv/bin/python analyze_mistakes.py --show-engine         # 使用するエンジン・モデルと照合結果
    .venv/bin/python analyze_mistakes.py --models              # モデル別の解析局数
    .venv/bin/python analyze_mistakes.py --regen-only          # README / AI_CONTEXT だけ作り直す
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

from analysis import schema
from storage import Storage, now_jst_iso

ROOT = Path(__file__).resolve().parent
log = logging.getLogger("mistakes")


# ------------------------------------------------------------------ 設定
def load_config() -> dict:
    return json.loads((ROOT / "config.json").read_text(encoding="utf-8"))


def build_params(cfg: dict, a: argparse.Namespace):
    from analysis.evaluator import Thresholds
    from analysis.runner import Params

    c = cfg.get("analysis", {})
    p1, p2 = c.get("pass1", {}), c.get("pass2", {})
    env = os.environ.get
    return Params(
        pass1_ms=a.pass1_ms or p1.get("movetime_ms") or 150,
        pass1_nodes=None if a.pass1_ms else p1.get("nodes"),
        pass2_ms=a.pass2_ms or p2.get("movetime_ms") or 2000,
        pass2_nodes=None if a.pass2_ms else p2.get("nodes"),
        pass2_multipv=int(p2.get("multipv", 3)),
        threads=int(a.threads or env("ANALYSIS_THREADS") or c.get("threads", 8)),
        hash_mb=int(env("ANALYSIS_HASH_MB") or c.get("hash_mb", 512)),
        scale=float(c.get("winrate_scale", 600)),
        thresholds=Thresholds.from_config(c.get("thresholds")),
        pv_moves=int(c.get("pv_moves", 6)),
        skip_opening_plies=int(c.get("skip_opening_plies", 0)),
        analysis_version=int(c.get("analysis_version", 1)),
    )


# ------------------------------------------------------------------ 対象選定
def select_targets(store: Storage, index: dict, a: argparse.Namespace, cfg: dict,
                   current_model: tuple[str, str] | None) -> list[tuple[dict, str]]:
    version = str(cfg.get("analysis", {}).get("analysis_version", 1))
    rows = sorted(store.rows, key=lambda r: (r["played_at"], r["game_id"]), reverse=True)
    out = []
    for r in rows:
        if a.game and r["game_id"] not in a.game:
            continue
        if a.since and r["played_at"][:10] < a.since:
            continue
        if a.mode and r["time_mode"] not in a.mode:
            continue
        if r.get("my_turn") not in ("SENTE", "GOTE") or not r.get("csa_rel_path"):
            continue
        done = index.get(r["game_id"])
        if a.force or a.game:
            reason = "指定" if done else "未解析"
        elif not done:
            reason = "未解析"
        elif done["csa_hash"] != r["csa_hash"]:
            reason = "棋譜が更新"
        elif done["analysis_version"] != version:
            reason = f"解析バージョン {done['analysis_version']}→{version}"
        elif a.reanalyze_model_mismatch and current_model and (done["model_id"], done["nn_bin_sha256"]) != current_model:
            reason = f"モデル {done['model_id']}→{current_model[0]}"
        else:
            continue
        out.append((r, reason))
    return out[: a.limit] if a.limit else out


# ------------------------------------------------------------------ 保存
def save_game(meta: dict, game, ga, p, info) -> dict:
    from analysis import report

    analyzed_at = now_jst_iso()
    gid = meta["game_id"]
    schema.write_csv(ROOT / schema.MOVES_DIR_REL / f"{gid}.csv", schema.MOVE_COLUMNS,
                     report.move_rows(game, ga, p, info))
    rp = ROOT / schema.report_rel(gid)
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(report.markdown(meta, game, ga, p, info, analyzed_at), encoding="utf-8")

    mpath = ROOT / schema.MISTAKES_REL
    rows = [r for r in schema.read_csv(mpath) if r["game_id"] != gid] + report.mistake_rows(meta, ga, p, info)
    rows.sort(key=lambda r: (r["played_at"], r["game_id"], int(r["ply"])))
    schema.write_csv(mpath, schema.MISTAKE_COLUMNS, rows)

    ipath = ROOT / schema.INDEX_REL
    idx = schema.load_index(ROOT)
    idx[gid] = report.index_row(meta, game, ga, p, info, analyzed_at)
    order = {r["game_id"]: (r["played_at"], r["game_id"]) for r in Storage(ROOT).rows}
    schema.write_csv(ipath, schema.INDEX_COLUMNS, sorted(idx.values(), key=lambda r: order.get(r["game_id"], ("", ""))))
    return idx[gid]


def regenerate(store: Storage, cfg: dict) -> None:
    store.write_readme(cfg["player_name"], cfg.get("recent_games_in_readme", 20), cfg.get("quiz_url"))
    store.write_ai_context(cfg["player_name"])
    log.info("README.md / %s を更新しました", Storage.AI_CONTEXT_REL)


def warn_if_behind() -> None:
    try:
        subprocess.run(["git", "fetch", "--quiet"], cwd=ROOT, check=True, timeout=30, capture_output=True)
        n = subprocess.run(["git", "rev-list", "--count", "HEAD..@{u}"], cwd=ROOT, check=True,
                           capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:  # noqa: BLE001 — オフラインなどは無視
        return
    if n and n != "0":
        log.warning("origin より %s コミット遅れています。先に `git pull` すると Actions が取得した最新の対局も解析できます", n)


# ------------------------------------------------------------------ サブコマンド
def cmd_models(index: dict) -> int:
    from analysis.env import EngineSetupError, get_model, load_lock

    lock = load_lock()
    try:
        cur_id, cur = get_model(lock)
    except EngineSetupError as e:
        print(e)
        return 1
    c = Counter((r["model_id"], r["model_name"], r["nn_bin_sha256"][:12]) for r in index.values())
    print(f"現在のモデル: {cur.get('display_name', cur_id)} [{cur_id}] nn.bin {cur.get('nn_bin_sha256', '')[:12] or '(未記入)'}")
    print(f"解析済み: {len(index)} 局")
    for (mid, name, sha), n in c.most_common():
        mark = "  ← 現在" if mid == cur_id and (not cur.get("nn_bin_sha256") or cur["nn_bin_sha256"].startswith(sha)) else ""
        print(f"  {name} [{mid}] sha:{sha}  {n} 局{mark}")
    return 0


def cmd_show_engine(p) -> int:
    from analysis.engine import UsiEngine
    from analysis.env import EngineSetupError, resolve

    try:
        info = resolve()
    except EngineSetupError as e:
        print(f"NG: {e}")
        return 1
    eng = UsiEngine(info.binary)
    try:
        eng.configure(info.eval_dir, 1, 64)
        info.engine_name = eng.name
    finally:
        eng.quit()
    print("OK: エンジンと評価関数はロックファイルと一致しています")
    print(f"  エンジン   : {info.engine_name}（{info.engine_tag}, commit {info.engine_commit[:12]}）")
    print(f"  バイナリ   : {info.binary}")
    print(f"  評価関数   : {info.model_name} [{info.model_id}]")
    print(f"  nn.bin     : {info.eval_dir / 'nn.bin'}")
    print(f"  SHA-256    : {info.nn_bin_sha256}")
    print(f"  解析設定   : 第1パス {p.pass1_limit} / 第2パス {p.pass2_limit} MultiPV {p.pass2_multipv} / "
          f"Threads {p.threads} / Hash {p.hash_mb}MB")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, help="解析する局数の上限（新しい順）")
    ap.add_argument("--game", action="append", help="対局 ID を指定（複数可）。解析済みでも再解析する")
    ap.add_argument("--since", help="この日付（YYYY-MM-DD）以降の対局のみ")
    ap.add_argument("--mode", action="append", help="持ち時間で絞る（shogi10 / shogi5 / shogi2。複数可）")
    ap.add_argument("--force", action="store_true", help="解析済みも含めて再解析")
    ap.add_argument("--reanalyze-model-mismatch", action="store_true", help="現在と違うモデルで解析した対局を再解析")
    ap.add_argument("--dry-run", action="store_true", help="対象の一覧を表示するだけ")
    ap.add_argument("--regen-only", action="store_true", help="README / AI_CONTEXT だけ作り直す")
    ap.add_argument("--show-engine", action="store_true", help="使用するエンジン・モデルの照合結果を表示")
    ap.add_argument("--models", action="store_true", help="モデル別の解析局数を表示")
    ap.add_argument("--threads", type=int, help="エンジンのスレッド数（設定ファイルを上書き）")
    ap.add_argument("--pass1-ms", type=int, help="第1パスの思考時間 ms（設定ファイルを上書き）")
    ap.add_argument("--pass2-ms", type=int, help="第2パスの思考時間 ms（設定ファイルを上書き）")
    ap.add_argument("--no-git-check", action="store_true", help="origin との差分チェックをしない")
    ap.add_argument("-v", "--verbose", action="store_true", help="エンジンとのやり取りを表示")
    a = ap.parse_args()
    logging.basicConfig(level=logging.DEBUG if a.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    cfg = load_config()
    cfg["player_name"] = (os.environ.get("SHOGI_QUEST_PLAYER") or cfg["player_name"]).strip()
    store = Storage(ROOT, cfg.get("data_dir", "data"))
    index = schema.load_index(ROOT)

    if a.regen_only:
        regenerate(store, cfg)
        return 0
    if a.models:
        return cmd_models(index)

    p = build_params(cfg, a)
    if a.show_engine:
        return cmd_show_engine(p)

    if not a.no_git_check:
        warn_if_behind()

    from analysis.env import EngineSetupError, resolve
    try:
        info = resolve()
    except EngineSetupError as e:
        if not a.dry_run:
            log.error("%s", e)
            return 2
        info = None

    targets = select_targets(store, index, a, cfg, (info.model_id, info.nn_bin_sha256) if info else None)
    est = sum(int(r["moves_count"] or 0) for r, _ in targets) * (p.pass1_ms or 150) / 1000 * 1.3
    log.info("解析対象 %d 局（第1パスだけで約 %.0f 分の見込み）", len(targets), est / 60)
    for r, reason in targets:
        log.info("  %s %s %-7s %s手 [%s]", r["played_at"][:16], r["game_id"], r["time_mode"], r["moves_count"], reason)
    if a.dry_run or not targets:
        return 0

    from analysis.engine import UsiEngine
    from analysis.kifu import load_game
    from analysis.runner import analyze_game

    eng = UsiEngine(info.binary)
    done = 0
    try:
        eng.configure(info.eval_dir, p.threads, p.hash_mb)
        info.engine_name = eng.name
        log.info("解析環境: %s", info.label)
        for i, (meta, _reason) in enumerate(targets, 1):
            log.info("[%d/%d] %s %s（%s）", i, len(targets), meta["played_at"][:16], meta["game_id"], meta["time_mode"])
            try:
                game = load_game(ROOT / meta["csa_rel_path"])
            except Exception as e:  # noqa: BLE001
                log.error("  棋譜を読めませんでした: %s", e)
                continue
            ga = analyze_game(eng, game, meta["my_turn"], p)
            row = save_game(meta, game, ga, p, info)
            done += 1
            log.info("  保存: %s（詰み逃し %s / 大悪手 %s / 悪手 %s / 疑問手 %s, %.0f秒）", schema.report_rel(meta["game_id"]),
                     row["n_mate_miss"], row["n_blunder"], row["n_mistake"], row["n_dubious"], ga.elapsed)
    except KeyboardInterrupt:
        log.warning("中断しました（解析済み %d 局は保存済み。次回は続きから再開します）", done)
    finally:
        eng.quit()
        if done:
            regenerate(Storage(ROOT, cfg.get("data_dir", "data")), cfg)
    log.info("完了: %d 局を解析しました。内容を確認して git add / commit / push してください", done)
    return 0


if __name__ == "__main__":
    sys.exit(main())
