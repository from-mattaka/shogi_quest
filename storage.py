"""CSV マスター（data/games_summary.csv）管理と README.md / AI_CONTEXT.md 生成。"""
from __future__ import annotations

import csv
import hashlib
import io
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from analysis import schema as an

JST = timezone(timedelta(hours=9))

COLUMNS = [
    "game_id", "time_mode", "played_at", "handicap",
    "sente_name", "sente_rating", "gote_name", "gote_rating",
    "my_turn", "my_rating", "opponent_name", "opponent_rating",
    "result", "moves_count", "end_reason",
    "csa_rel_path", "csa_hash", "fetched_at",
]

COLUMN_SPEC = [
    ("game_id", "str", "将棋クエストの対局 ID（英数字12桁程度）。主キー"),
    ("time_mode", "str", "`shogi10` / `shogi5` / `shogi2`（10分 / 5分 / 2分切れ負け）"),
    ("played_at", "str (datetime)", "対局開始日時 `YYYY-MM-DD HH:MM:SS`（JST。API の UTC を変換）"),
    ("handicap", "str", "手合い `平手` / `香落ち` / `角落ち` / `飛車落ち` / `飛香落ち` / `二枚落ち`"),
    ("sente_name", "str", "先手の表示名（相手の場合は `相手` に置換）"),
    ("sente_rating", "int / 空", "先手の対局時レート"),
    ("gote_name", "str", "後手の表示名（相手の場合は `相手` に置換）"),
    ("gote_rating", "int / 空", "後手の対局時レート"),
    ("my_turn", "str", "自分の手番 `SENTE` / `GOTE`"),
    ("my_rating", "int / 空", "自分の対局時レート"),
    ("opponent_name", "str", "常に `相手`（相手のユーザー名は公開しない方針で伏せている）"),
    ("opponent_rating", "int / 空", "相手の対局時レート"),
    ("result", "str", "自分から見た結果 `WIN` / `LOSS` / `DRAW`"),
    ("moves_count", "int", "CSA 内の実際の指し手数（投了・時間切れ等の終局アクションは含まない）"),
    ("end_reason", "str", "終局理由 `投了` / `時間切れ` / `詰み` / `トライ` / `切断` / `千日手` / `反則` / `連続王手千日手`"),
    ("csa_rel_path", "str", "リポジトリルートからの CSA 相対パス `data/csa/{time_mode}/{game_id}.csa`"),
    ("csa_hash", "str", "CSA ファイル（UTF-8, LF）の SHA-256 16進"),
    ("fetched_at", "str (ISO8601)", "取得日時（JST, `+09:00` 付き）"),
]

TIME_MODE_LABELS = {"shogi10": "10分", "shogi5": "5分", "shogi2": "2分"}


def now_jst_iso() -> str:
    return datetime.now(JST).replace(microsecond=0).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _int(v) -> int | None:
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _md(v) -> str:
    return str(v if v not in (None, "") else "-").replace("|", "\\|").replace("\n", " ")


def _rate(w: int, n: int) -> str:
    return f"{w / n * 100:.1f}%" if n else "-"


def _f(v) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


class Storage:
    AI_CONTEXT_REL = "docs/ai/AI_CONTEXT.md"

    def __init__(self, root: Path, data_dir: str = "data"):
        self.root = Path(root)
        self.data_dir = self.root / data_dir
        self.csv_path = self.data_dir / "games_summary.csv"
        self.csa_dir = self.data_dir / "csa"
        self.rows: list[dict] = []
        self.ids: set[str] = set()
        self.is_first_run = not self.csv_path.exists()
        self._load()
        self.analysis = an.load_index(self.root)  # game_id → analysis_index.csv の行（ローカル解析の結果）

    # ---------------------------------------------------------- master CSV
    def _load(self) -> None:
        if self.is_first_run:
            return
        with self.csv_path.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                self.rows.append({c: r.get(c, "") for c in COLUMNS})
                self.ids.add(r["game_id"])

    def exists(self, game_id: str) -> bool:
        return game_id in self.ids  # O(1)

    def save_csa(self, time_mode: str, game_id: str, text: str) -> tuple[str, str]:
        path = self.csa_dir / time_mode / f"{game_id}.csa"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        return path.relative_to(self.root).as_posix(), sha256_text(text)

    def add(self, row: dict) -> bool:
        if row["game_id"] in self.ids:
            return False
        self.rows.append({c: ("" if row.get(c) is None else row.get(c)) for c in COLUMNS})
        self.ids.add(row["game_id"])
        return True

    def save(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.rows.sort(key=lambda r: (r["played_at"], r["game_id"]))
        tmp = self.csv_path.with_suffix(".csv.tmp")
        with tmp.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
            w.writeheader()
            w.writerows(self.rows)
        tmp.replace(self.csv_path)

    # ---------------------------------------------------------- stats
    def _by_mode(self) -> dict[str, list[dict]]:
        d: dict[str, list[dict]] = defaultdict(list)
        for r in self.rows:
            d[r["time_mode"]].append(r)
        order = list(TIME_MODE_LABELS) + sorted(k for k in d if k not in TIME_MODE_LABELS)
        return {k: sorted(d[k], key=lambda r: r["played_at"]) for k in order if k in d}

    @staticmethod
    def _mode_stats(rows: list[dict]) -> dict:
        c = Counter(r["result"] for r in rows)
        moves = [m for m in (_int(r["moves_count"]) for r in rows) if m is not None]
        rates = [x for x in (_int(r["my_rating"]) for r in rows) if x is not None]
        latest = next((_int(r["my_rating"]) for r in reversed(rows) if _int(r["my_rating"]) is not None), None)
        dates = [r["played_at"] for r in rows if r["played_at"]]
        n = len(rows)
        return {
            "n": n, "win": c["WIN"], "loss": c["LOSS"], "draw": c["DRAW"],
            "win_rate": _rate(c["WIN"], c["WIN"] + c["LOSS"]),
            "avg_moves": f"{sum(moves) / len(moves):.1f}" if moves else "-",
            "latest_rating": latest if latest is not None else "-",
            "rating_range": f"{min(rates)}〜{max(rates)}" if rates else "-",
            "period": f"{min(dates)[:10]} 〜 {max(dates)[:10]}" if dates else "-",
        }

    def _recent(self, n: int) -> list[dict]:
        return sorted(self.rows, key=lambda r: (r["played_at"], r["game_id"]), reverse=True)[:n]

    def updated_at(self) -> str:
        """データ由来の最終更新日時（実行時刻ではないので、変化が無ければ生成物も変わらない）。"""
        ts = [r["fetched_at"] for r in self.rows if r["fetched_at"]]
        ts += [r["analyzed_at"] for r in self.analysis.values() if r.get("analyzed_at")]
        return max(ts) if ts else "-"

    def _analysis_summary(self) -> list[dict]:
        """モデル × time_mode 別の悪手集計。異なるモデルの数値は混ぜない。"""
        mode_of = {r["game_id"]: r["time_mode"] for r in self.rows}
        grp: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
        for gid, a in self.analysis.items():
            if gid in mode_of:
                grp[(a["model_name"], a["model_id"], mode_of[gid])].append(a)
        out = []
        for (name, mid, mode), rows in sorted(grp.items()):
            n = len(rows)
            moves = sum(_int(r["my_moves"]) or 0 for r in rows)
            c = {k: sum(_int(r[k]) or 0 for r in rows) for k in an.CATEGORY_COUNT_COL.values()}
            bad = c["n_blunder"] + c["n_mistake"]
            allc = bad + c["n_dubious"] + c["n_mate_miss"]
            out.append({
                "model": f"{name} (`{mid}`)", "mode": mode, "games": n, "my_moves": moves, **c,
                "bad_rate": _rate(bad, moves), "all_rate": _rate(allc, moves),
                "bad_per_game": f"{bad / n:.2f}" if n else "-", "all_per_game": f"{allc / n:.2f}" if n else "-",
            })
        return out

    def _analysis_cell(self, game_id: str, link_prefix: str = "") -> str:
        a = self.analysis.get(game_id)
        if not a:
            return "-"
        counts = " ".join(f"{an.CATEGORY_SHORT[c]}{a[an.CATEGORY_COUNT_COL[c]]}" for c in an.CATEGORIES)
        return f"[{_md(a['model_name'])}]({link_prefix}{an.report_rel(game_id)}) {counts}"

    # ---------------------------------------------------------- README.md
    def write_readme(self, player: str, recent_n: int = 20) -> None:
        by_mode = self._by_mode()
        L = [
            f"# 将棋クエスト対局記録 — {player}",
            "",
            f"最終更新: {self.updated_at()}　/　総対局数: **{len(self.rows)}**　/　悪手検出済み: **{len(self.analysis)}**",
            "",
            "> 対局は GitHub Actions が毎日自動収集し、悪手検出（将棋AIによる解析）はローカルで手動実行しています。生データ: "
            f"[`data/games_summary.csv`](data/games_summary.csv)　AI 相談用: [`AI_CONTEXT.md`]({self.AI_CONTEXT_REL})　"
            "悪手検出の説明: [`docs/mistake_analysis.md`](docs/mistake_analysis.md)",
            "",
            "## 持ち時間別サマリー",
            "",
            "| 持ち時間 | 対局数 | 勝 | 負 | 分 | 勝率 | 最新レート | 平均手数 |",
            "|---|--:|--:|--:|--:|--:|--:|--:|",
        ]
        for mode in TIME_MODE_LABELS:
            s = self._mode_stats(by_mode.get(mode, []))
            L.append(
                f"| {TIME_MODE_LABELS[mode]} | {s['n']} | {s['win']} | {s['loss']} | {s['draw']} "
                f"| {s['win_rate']} | {s['latest_rating']} | {s['avg_moves']} |"
            )
        L += [
            "",
            "勝率は引き分けを除いた `勝 / (勝 + 負)`。",
            "",
            f"## 直近{recent_n}局",
            "",
            "| 日時 | 持ち時間 | 手番 | 相手 | 結果 | 手数 | 終局理由 | 自レート | 棋譜 | 悪手検出 |",
            "|---|---|---|---|:-:|--:|---|--:|---|---|",
        ]
        mark = {"WIN": "○ 勝", "LOSS": "● 負", "DRAW": "△ 分"}
        turn = {"SENTE": "☗先", "GOTE": "☖後"}
        for r in self._recent(recent_n):
            opp = f"{r['opponent_name']}({r['opponent_rating']})" if r["opponent_rating"] else r["opponent_name"]
            link = f"[CSA]({r['csa_rel_path']})" if r["csa_rel_path"] else "-"
            L.append(
                f"| {_md(r['played_at'][:16])} | {TIME_MODE_LABELS.get(r['time_mode'], r['time_mode'])} "
                f"| {turn.get(r['my_turn'], '-')} | {_md(opp)} | {mark.get(r['result'], '-')} "
                f"| {_md(r['moves_count'])} | {_md(r['end_reason'])} | {_md(r['my_rating'])} | {link} "
                f"| {self._analysis_cell(r['game_id'])} |"
            )
        L += ["", "悪手検出の列: 評価関数名（レポートへのリンク）と、"
              + "・".join(f"{an.CATEGORY_SHORT[c]}={c}" for c in an.CATEGORIES) + " の件数。"]
        summary = self._analysis_summary()
        if summary:
            L += [
                "",
                "## 悪手検出サマリー（評価関数・持ち時間別）",
                "",
                "| 評価関数 | 持ち時間 | 解析局数 | 自分の手数 | 詰み逃し | 大悪手 | 悪手 | 疑問手 | 悪手率 | 1局あたり悪手 |",
                "|---|---|--:|--:|--:|--:|--:|--:|--:|--:|",
            ]
            for s in summary:
                L.append(
                    f"| {s['model']} | {TIME_MODE_LABELS.get(s['mode'], s['mode'])} | {s['games']} | {s['my_moves']} "
                    f"| {s['n_mate_miss']} | {s['n_blunder']} | {s['n_mistake']} | {s['n_dubious']} "
                    f"| {s['bad_rate']} | {s['bad_per_game']} |"
                )
            L += ["", "悪手率 = (大悪手 + 悪手) / 自分の手数。一覧: "
                  f"[`{an.MISTAKES_REL}`]({an.MISTAKES_REL})"]
        (self.root / "README.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    # ---------------------------------------------------------- AI_CONTEXT.md
    def write_ai_context(self, player: str) -> None:
        by_mode = self._by_mode()
        L = [
            "# AI_CONTEXT — 将棋クエスト対局データ仕様書",
            "",
            "このファイルは生成 AI に対局傾向の分析を相談する際のインプット用です。"
            "リポジトリ構造・データ定義・現在の統計・実データのサンプルをまとめています。",
            "",
            f"- 対象プレイヤー: `{player}`",
            f"- データ更新日時: {self.updated_at()}",
            f"- 総対局数: {len(self.rows)}（うち悪手検出済み {len(self.analysis)}）",
            "",
            "## 1. ファイル配置",
            "",
            "```text",
            ".",
            "├── data/",
            "│   ├── games_summary.csv        # 全対局のマスター（UTF-8, ヘッダ行あり, LF, played_at 昇順）",
            "│   ├── csa/",
            "│   │   ├── shogi10/{game_id}.csa  # 10分切れ負けの棋譜",
            "│   │   ├── shogi5/{game_id}.csa   # 5分切れ負けの棋譜",
            "│   │   └── shogi2/{game_id}.csa   # 2分切れ負けの棋譜",
            "│   └── analysis/                # 将棋AIによる悪手検出の結果（analyze_mistakes.py をローカルで手動実行して追加）",
            "│       ├── analysis_index.csv   # 解析済み対局の台帳（使用エンジン・評価関数・件数）",
            "│       ├── mistakes.csv         # 悪手・疑問手の一覧（全対局分）",
            "│       ├── moves/{game_id}.csv  # 1手ごとの評価値・期待勝率の推移",
            "│       └── reports/{game_id}.md # 対局別の解析レポート（盤面図・候補手つき）",
            "├── docs/",
            "│   ├── mistake_analysis.md      # 悪手検出（analyze_mistakes.py）の説明",
            "│   ├── engine_model.md          # 評価関数の確認・切り替え手順",
            "│   └── ai/AI_CONTEXT.md         # 本ファイル（自動生成）",
            "└── README.md                    # 閲覧用ダッシュボード（自動生成）",
            "```",
            "",
            "- CSA ファイルは UTF-8・改行 LF。相手のユーザー名は `N+相手(レート)` のように伏せている。将棋クエストの CSA には終局行（`%TORYO` 等）が無いため、勝敗・終局理由は CSV 側を参照。",
            "- `games_summary.csv` の 1 行 = 1 対局。`csa_rel_path` で棋譜と 1:1 対応。",
            "",
            "## 2. games_summary.csv カラム定義",
            "",
            "| # | カラム | 型 | 格納ルール |",
            "|--:|---|---|---|",
        ]
        for i, (c, t, d) in enumerate(COLUMN_SPEC, 1):
            L.append(f"| {i} | `{c}` | {t} | {d} |")
        L += [
            "",
            "- 空値は空文字列（CSV 上は `,,`）。数値列も欠損時は空。",
            "- `sente_*` / `gote_*` は盤上の手番基準、`my_*` / `opponent_*` は自分基準の重複表現。レートは対局開始時点の値。",
            "",
            "## 3. 統計サマリー",
            "",
            "### ① time_mode 別",
            "",
            "| time_mode | 局数 | 勝 | 負 | 分 | 勝率 | 平均手数 | 自レート範囲 | 最新レート | 期間 |",
            "|---|--:|--:|--:|--:|--:|--:|---|--:|---|",
        ]
        for mode, rows in by_mode.items():
            s = self._mode_stats(rows)
            L.append(
                f"| {mode} | {s['n']} | {s['win']} | {s['loss']} | {s['draw']} | {s['win_rate']} "
                f"| {s['avg_moves']} | {s['rating_range']} | {s['latest_rating']} | {s['period']} |"
            )
        L += [
            "",
            "### ② time_mode × end_reason 別の勝敗件数",
            "",
            "| time_mode | end_reason | 勝 | 負 | 分 | 計 |",
            "|---|---|--:|--:|--:|--:|",
        ]
        for mode, rows in by_mode.items():
            grp: dict[str, Counter] = defaultdict(Counter)
            for r in rows:
                grp[r["end_reason"] or "(空)"][r["result"]] += 1
            for reason, c in sorted(grp.items(), key=lambda kv: -sum(kv[1].values())):
                L.append(
                    f"| {mode} | {_md(reason)} | {c['WIN']} | {c['LOSS']} | {c['DRAW']} | {sum(c.values())} |"
                )
        handicaps = Counter(r["handicap"] or "(空)" for r in self.rows)
        reasons = Counter(r["end_reason"] or "(空)" for r in self.rows)
        L += [
            "",
            "### ③ ユニーク値一覧",
            "",
            "- `handicap`: " + ", ".join(f"`{k}` ({v})" for k, v in handicaps.most_common()),
            "- `end_reason`: " + ", ".join(f"`{k}` ({v})" for k, v in reasons.most_common()),
            "",
            "## 4. 最新3件のデータサンプル",
            "",
            "### CSV",
            "",
            "```csv",
        ]
        latest3 = self._recent(3)
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(latest3)
        L += [buf.getvalue().rstrip("\n"), "```", "", "### 表", ""]
        L.append("| " + " | ".join(COLUMNS) + " |")
        L.append("|" + "---|" * len(COLUMNS))
        for r in latest3:
            L.append("| " + " | ".join(_md(r[c]) for c in COLUMNS) + " |")

        L += ["", "## 5. 最新 CSA 棋譜（1局分・全文）", ""]
        latest_csa = next(
            (r for r in self._recent(len(self.rows)) if r["csa_rel_path"] and (self.root / r["csa_rel_path"]).exists()),
            None,
        )
        if latest_csa:
            text = (self.root / latest_csa["csa_rel_path"]).read_text(encoding="utf-8")
            L += [
                f"`{latest_csa['csa_rel_path']}`（{latest_csa['played_at']} / {latest_csa['time_mode']} / "
                f"自分={latest_csa['my_turn']} / {latest_csa['result']}）",
                "",
                "```csa",
                text.rstrip("\n"),
                "```",
            ]
        else:
            L.append("（CSA ファイルはまだありません）")
        L += self._ai_context_analysis()
        path = self.root / self.AI_CONTEXT_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(L) + "\n", encoding="utf-8")

    def _ai_context_analysis(self) -> list[str]:
        def spec_table(spec):
            out = ["| # | カラム | 型 | 内容 |", "|--:|---|---|---|"]
            out += [f"| {i} | `{c}` | {t} | {d or '同上'} |" for i, (c, t, d) in enumerate(spec, 1)]
            return out

        L = [
            "",
            "## 6. 悪手検出データ（analyze_mistakes.py: 将棋AIによる悪手・疑問手の抽出）",
            "",
            "やねうら王＋評価関数（水匠など）で全手を評価し、自分の手のうち期待勝率を大きく下げた手を抽出したもの。"
            "解析方法の詳細は `docs/mistake_analysis.md`。",
            "",
            "- 期待勝率 W(E) = 1 / (1 + exp(−E/600))（E は自分視点の評価値 cp。自分から詰みあり=1、詰まされ=0）",
            "- 判定: `詰み逃し`（着手前に自分から詰みがあったのに逃した）/ `大悪手`（低下 ≥20pt）/ "
            "`悪手`（≥10pt）/ `疑問手`（≥5pt）。実戦手が AI 最善手と同じ場合は対象外",
            "- 2段階探索: 第1パスで全局面を短時間評価 → 候補局面のみ第2パスで長時間・MultiPV 3 で再評価し判定を確定",
            "- **評価関数が異なる解析結果は数値の基準が異なる**ため、集計は `model_id` ごとに分けて扱うこと",
            "",
        ]
        if not self.analysis:
            return L + ["（まだ解析済みの対局はありません）"]
        L += [
            "### ① 集計（評価関数 × time_mode 別）",
            "",
            "| 評価関数 | time_mode | 解析局数 | 自分の手数 | 詰み逃し | 大悪手 | 悪手 | 疑問手 | 悪手率 | 疑問手以上率 | 1局あたり悪手 | 1局あたり疑問手以上 |",
            "|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|",
        ]
        for s in self._analysis_summary():
            L.append(
                f"| {s['model']} | {s['mode']} | {s['games']} | {s['my_moves']} | {s['n_mate_miss']} | {s['n_blunder']} "
                f"| {s['n_mistake']} | {s['n_dubious']} | {s['bad_rate']} | {s['all_rate']} "
                f"| {s['bad_per_game']} | {s['all_per_game']} |"
            )
        L += [
            "",
            "悪手率 = (大悪手 + 悪手) / 自分の手数、疑問手以上率 = (詰み逃し + 大悪手 + 悪手 + 疑問手) / 自分の手数。",
            "",
            "### ② 勝敗別の 1 局あたり件数",
            "",
            "| 評価関数 | 結果 | 局数 | 1局あたり大悪手 | 1局あたり悪手 | 1局あたり疑問手 | 1局あたり詰み逃し |",
            "|---|---|--:|--:|--:|--:|--:|",
        ]
        res_of = {r["game_id"]: r["result"] for r in self.rows}
        grp: dict[tuple[str, str], list[dict]] = defaultdict(list)
        for gid, a in self.analysis.items():
            grp[(f"{a['model_name']} (`{a['model_id']}`)", res_of.get(gid, ""))].append(a)
        for (model, res), rows in sorted(grp.items()):
            n = len(rows)
            avg = {k: sum(_int(r[k]) or 0 for r in rows) / n for k in an.CATEGORY_COUNT_COL.values()}
            L.append(f"| {model} | {res or '-'} | {n} | {avg['n_blunder']:.2f} | {avg['n_mistake']:.2f} "
                     f"| {avg['n_dubious']:.2f} | {avg['n_mate_miss']:.2f} |")

        mistakes = an.read_csv(self.root / an.MISTAKES_REL)
        L += ["", "### ③ 評価値が大きく動いた局面の傾向（手数帯 × カテゴリ）", "",
              "| 手数帯 | " + " | ".join(an.CATEGORIES) + " |", "|---|" + "--:|" * len(an.CATEGORIES)]
        bands = [(1, 30), (31, 60), (61, 90), (91, 120), (121, 9999)]
        for lo, hi in bands:
            c = Counter(m["category"] for m in mistakes if lo <= (_int(m["ply"]) or 0) <= hi)
            label = f"{lo}〜{hi}手" if hi < 9999 else f"{lo}手〜"
            L.append(f"| {label} | " + " | ".join(str(c[k]) for k in an.CATEGORIES) + " |")

        L += ["", f"### ④ `{an.INDEX_REL}` カラム定義（1 行 = 解析済み 1 対局）", ""] + spec_table(an.INDEX_SPEC)
        L += ["", f"### ⑤ `{an.MISTAKES_REL}` カラム定義（1 行 = 抽出された 1 手）", ""] + spec_table(an.MISTAKE_SPEC)
        L += ["", f"### ⑥ `{an.MOVES_DIR_REL}/{{game_id}}.csv` カラム定義（1 行 = 1 手）", ""] + spec_table(an.MOVE_SPEC)

        worst = sorted(mistakes, key=lambda m: -_f(m["winrate_drop"]))[:5]
        if worst:
            L += ["", "### ⑦ 低下幅が大きい手 上位5件（mistakes.csv の抜粋）", "", "```csv"]
            buf = io.StringIO()
            w = csv.DictWriter(buf, fieldnames=an.MISTAKE_COLUMNS, lineterminator="\n", extrasaction="ignore")
            w.writeheader()
            w.writerows(worst)
            L += [buf.getvalue().rstrip("\n"), "```"]
        return L
