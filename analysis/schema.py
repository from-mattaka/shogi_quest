"""解析結果ファイルのパス・カラム定義（標準ライブラリのみ。Actions 側からも参照される）。"""
from __future__ import annotations

import csv
from pathlib import Path

ANALYSIS_DIR = "data/analysis"
INDEX_REL = f"{ANALYSIS_DIR}/analysis_index.csv"
MISTAKES_REL = f"{ANALYSIS_DIR}/mistakes.csv"
MOVES_DIR_REL = f"{ANALYSIS_DIR}/moves"
REPORTS_DIR_REL = f"{ANALYSIS_DIR}/reports"

# 判定カテゴリ（重い順）。CSV にはこの日本語ラベルで入る
CATEGORIES = ["詰み逃し", "大悪手", "悪手", "疑問手"]
CATEGORY_SHORT = {"詰み逃し": "逃", "大悪手": "大", "悪手": "悪", "疑問手": "疑"}
CATEGORY_COUNT_COL = {"詰み逃し": "n_mate_miss", "大悪手": "n_blunder", "悪手": "n_mistake", "疑問手": "n_dubious"}

INDEX_SPEC = [
    ("game_id", "str", "対局 ID（games_summary.csv と同じ）。主キー"),
    ("csa_hash", "str", "解析時点の CSA の SHA-256。games_summary.csv と異なれば再解析対象"),
    ("analysis_version", "int", "判定ロジックのバージョン（config.json の analysis.analysis_version）"),
    ("engine_name", "str", "エンジンが USI で返した名前（`id name`）"),
    ("engine_tag", "str", "やねうら王のビルド元タグとビルド種別（例: `V9.00/YANEURAOU_ENGINE_NNUE/AVX2`）"),
    ("model_id", "str", "評価関数の ID（engine/engine.lock.json の models のキー。例: `suisho5`）"),
    ("model_name", "str", "評価関数の表示名（例: `水匠5`）"),
    ("nn_bin_sha256", "str", "解析に実際に使った nn.bin の SHA-256（解析時に計算）"),
    ("pass1_limit", "str", "第1パスの探索制限（例: `movetime=150ms` / `nodes=300000`）"),
    ("pass2_limit", "str", "第2パスの探索制限"),
    ("pass2_multipv", "int", "第2パスの候補手数"),
    ("threads", "int", "エンジンのスレッド数"),
    ("hash_mb", "int", "置換表サイズ (MB)"),
    ("my_moves", "int", "自分の指し手数（判定対象の手数）"),
    ("n_candidates", "int", "第1パスで深掘り対象になった局面数"),
    ("n_mate_miss", "int", "詰み逃しの数"),
    ("n_blunder", "int", "大悪手の数"),
    ("n_mistake", "int", "悪手の数"),
    ("n_dubious", "int", "疑問手の数"),
    ("elapsed_sec", "float", "1局の解析にかかった秒数"),
    ("analyzed_at", "str (ISO8601)", "解析日時（JST）"),
]
INDEX_COLUMNS = [c for c, _, _ in INDEX_SPEC]

MISTAKE_SPEC = [
    ("game_id", "str", "対局 ID"),
    ("played_at", "str", "対局日時（JST）"),
    ("time_mode", "str", "`shogi10` / `shogi5` / `shogi2`"),
    ("my_turn", "str", "自分の手番 `SENTE` / `GOTE`"),
    ("ply", "int", "手数（その手が何手目か）"),
    ("category", "str", "`詰み逃し` / `大悪手` / `悪手` / `疑問手`"),
    ("winrate_before", "float", "着手前の期待勝率（自分視点, 0〜1）"),
    ("winrate_after", "float", "着手後の期待勝率（自分視点, 0〜1）"),
    ("winrate_drop", "float", "期待勝率の低下幅 = before − after"),
    ("eval_before", "str", "着手前の評価値（自分視点）。`+350` のような cp、詰みは `#+5`（5手で詰ませる）/`#-3`（3手で詰まされる）"),
    ("eval_after", "str", "着手後の評価値（自分視点, 同上）"),
    ("move_usi", "str", "実戦の指し手（USI 形式）"),
    ("move_ja", "str", "実戦の指し手（日本語。`▲７六歩(77)` 形式）"),
    ("reply_pv", "str", "実戦手の後の相手からの反撃手順（読み筋の先頭, 日本語, 空白区切り）"),
    ("cand1_move", "str", "AI 推奨1位の指し手（日本語）"),
    ("cand1_usi", "str", "AI 推奨1位の指し手（USI）"),
    ("cand1_eval", "str", "AI 推奨1位を指した場合の評価値（自分視点）"),
    ("cand1_pv", "str", "AI 推奨1位の読み筋（日本語, 空白区切り）"),
    ("cand2_move", "str", "2位（以下同様。候補が無い場合は空）"),
    ("cand2_usi", "str", ""),
    ("cand2_eval", "str", ""),
    ("cand2_pv", "str", ""),
    ("cand3_move", "str", "3位"),
    ("cand3_usi", "str", ""),
    ("cand3_eval", "str", ""),
    ("cand3_pv", "str", ""),
    ("sfen_before", "str", "着手直前の局面（SFEN）"),
    ("model_id", "str", "解析に使った評価関数の ID"),
    ("nn_bin_sha12", "str", "解析に使った nn.bin の SHA-256 先頭12文字"),
]
MISTAKE_COLUMNS = [c for c, _, _ in MISTAKE_SPEC]

MOVE_SPEC = [
    ("ply", "int", "手数。0 は開始局面"),
    ("mover", "str", "その手を指した側 `SENTE` / `GOTE`（ply 0 は空）"),
    ("is_my_move", "int", "自分の手なら 1"),
    ("move_usi", "str", "指し手（USI）"),
    ("move_ja", "str", "指し手（日本語）"),
    ("best_usi", "str", "着手前の局面での第1パス最善手（USI）"),
    ("best_ja", "str", "同（日本語）"),
    ("eval", "str", "着手後の評価値（自分視点。形式は mistakes.csv の eval_* と同じ）"),
    ("winrate", "float", "着手後の期待勝率（自分視点）"),
    ("winrate_drop", "float", "自分の手のみ: 着手前後の期待勝率の低下幅（第1パス値）"),
    ("category", "str", "第2パスで判定が確定した場合のカテゴリ"),
    ("model_id", "str", "評価関数の ID"),
]
MOVE_COLUMNS = [c for c, _, _ in MOVE_SPEC]


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, columns: list[str], rows: list[dict]) -> None:
    """一時ファイルに書いてから置き換える（途中で中断しても壊れない）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({c: ("" if r.get(c) is None else r.get(c)) for c in columns})
    tmp.replace(path)


def load_index(root: Path) -> dict[str, dict]:
    return {r["game_id"]: r for r in read_csv(Path(root) / INDEX_REL)}


def report_rel(game_id: str) -> str:
    return f"{REPORTS_DIR_REL}/{game_id}.md"
