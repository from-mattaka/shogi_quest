"""対局相手のユーザー名を伏せる（公開リポジトリに他人のハンドル名を載せないため）。

- 収集時: collect.py が CSA 保存前・CSV 行作成時にここの関数を通す。
- 既存データ: `python anonymize.py` で data/ 配下を一括変換し、README / AI_CONTEXT を作り直す。
  何度実行しても結果は同じ（冪等）。

レートは残す（棋力の目安として分析に使うため）。自分の名前（config の player_name）はそのまま。
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
from pathlib import Path

OPPONENT_LABEL = "相手"

# CSA の対局者行: N+名前(1500) / N-名前(1500)
_CSA_NAME_RE = re.compile(r"^(N[+-])(.*?)(\s*[\(（]\s*\d+\s*[\)）]\s*)?$")


def is_me(name: str, me: str) -> bool:
    return (name or "").strip().lower() == me.strip().lower()


def anonymize_csa(text: str, me: str) -> str:
    """N+ / N- 行のうち自分以外の名前を OPPONENT_LABEL に置き換える。"""
    out = []
    for line in text.split("\n"):
        m = _CSA_NAME_RE.match(line)
        if m and not is_me(m.group(2), me):
            line = f"{m.group(1)}{OPPONENT_LABEL}{m.group(3) or ''}"
        out.append(line)
    return "\n".join(out)


def anonymize_row(row: dict, me: str) -> dict:
    """games_summary.csv の 1 行から相手名を伏せる。"""
    row = dict(row)
    for col in ("sente_name", "gote_name"):
        if row.get(col) and not is_me(row[col], me):
            row[col] = OPPONENT_LABEL
    if row.get("opponent_name"):
        row["opponent_name"] = OPPONENT_LABEL
    return row


# ---------------------------------------------------------------- 既存データの一括変換
_REPORT_OPP_RE = re.compile(r"^\| 相手 \| .*?((?:（\d+）)?) \|$", re.M)


def migrate(root: Path, me: str) -> None:
    from analysis import schema as an
    from storage import COLUMNS, Storage, sha256_text

    data = root / "data"
    summary = data / "games_summary.csv"
    index_path = root / an.INDEX_REL

    # 1) CSA を書き換え、新しいハッシュを控える（解析台帳の csa_hash も合わせ、再解析を起こさない）
    new_hash: dict[str, str] = {}
    for p in sorted((data / "csa").rglob("*.csa")):
        text = p.read_text(encoding="utf-8")
        anon = anonymize_csa(text, me)
        if anon != text:
            p.write_text(anon, encoding="utf-8", newline="\n")
        new_hash[p.relative_to(root).as_posix()] = sha256_text(anon)

    # 2) games_summary.csv
    with summary.open(encoding="utf-8", newline="") as f:
        rows = [anonymize_row(r, me) for r in csv.DictReader(f)]
    hash_by_gid: dict[str, tuple[str, str]] = {}
    for r in rows:
        if r["csa_rel_path"] in new_hash:
            hash_by_gid[r["game_id"]] = (r["csa_hash"], new_hash[r["csa_rel_path"]])
            r["csa_hash"] = new_hash[r["csa_rel_path"]]
    with summary.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    # 3) 解析台帳: 解析時と同じ棋譜（旧ハッシュ一致）なら新ハッシュに付け替える
    if index_path.exists():
        with index_path.open(encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            fields = reader.fieldnames
            idx = list(reader)
        for r in idx:
            old_new = hash_by_gid.get(r["game_id"])
            if old_new and r["csa_hash"] == old_new[0]:
                r["csa_hash"] = old_new[1]
        with index_path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
            w.writeheader()
            w.writerows(idx)

    # 4) 解析レポートの「相手」行（レートは残す）
    for p in sorted((root / an.REPORTS_DIR_REL).glob("*.md")):
        text = p.read_text(encoding="utf-8")
        anon = _REPORT_OPP_RE.sub(lambda m: f"| 相手 | {OPPONENT_LABEL}{m.group(1)} |", text)
        if anon != text:
            p.write_text(anon, encoding="utf-8", newline="\n")

    # 5) README / AI_CONTEXT を作り直す
    cfg = json.loads((root / "config.json").read_text(encoding="utf-8"))
    store = Storage(root, cfg.get("data_dir", "data"))
    store.write_readme(me, cfg.get("recent_games_in_readme", 20), cfg.get("quiz_url"))
    store.write_ai_context(me)
    print(f"CSA {len(new_hash)} 件、CSV {len(rows)} 行を処理しました")


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    cfg = json.loads((root / "config.json").read_text(encoding="utf-8"))
    me = (os.environ.get("SHOGI_QUEST_PLAYER") or cfg["player_name"]).strip()
    migrate(root, me)
    sys.exit(0)
