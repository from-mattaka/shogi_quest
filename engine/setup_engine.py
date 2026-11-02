"""やねうら王のビルドと評価関数（水匠など）の取得を行うセットアップスクリプト。

何度実行しても安全（導入済みでロックファイルと一致していれば何もしない）。
書き込むのは .engine/ 配下（環境変数 SHOGI_ENGINE_DIR で変更可）と、
engine.lock.json の nn_bin_sha256 が空のときの初回記入だけ。sudo は使わない。

使い方:
    .venv/bin/python engine/setup_engine.py              # active_model を導入
    .venv/bin/python engine/setup_engine.py --model ID   # 指定モデルを導入
    .venv/bin/python engine/setup_engine.py --check      # 照合だけ行う（何もダウンロードしない）
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from analysis.env import (  # noqa: E402
    BINARY_NAME, LOCK_PATH, EngineSetupError, binary_path, engine_dir, get_model, load_lock,
    model_dir, resolve, sha256_file,
)

JST = timezone(timedelta(hours=9))


def now() -> str:
    return datetime.now(JST).replace(microsecond=0).isoformat()


def run(cmd: list[str], **kw) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, **kw)


def require_tools(*names: str) -> None:
    missing = [n for n in names if shutil.which(n) is None]
    if missing:
        raise SystemExit(f"必要なコマンドがありません: {', '.join(missing)}（devcontainer の再ビルドで導入されます）")


# ------------------------------------------------------------------ engine
def build_engine(lock: dict, model: dict, keep_src: bool) -> Path:
    dest = binary_path(lock, model)
    if dest.exists():
        print(f"[engine] ビルド済み: {dest}")
        return dest

    e = lock["engine"]
    require_tools("git", "make", e["compiler"])
    src = engine_dir() / "src" / e["tag"]
    if src.exists():
        shutil.rmtree(src)
    src.parent.mkdir(parents=True, exist_ok=True)

    run(["git", "clone", "--depth", "1", "--branch", e["tag"], e["repo"], str(src)])
    head = subprocess.run(["git", "-C", str(src), "rev-parse", "HEAD"], check=True,
                          capture_output=True, text=True).stdout.strip()
    if e.get("commit") and head != e["commit"]:
        raise SystemExit(f"タグ {e['tag']} のコミットがロックと異なります（取得 {head} / lock {e['commit']}）。中止します")

    jobs = str(max(1, (os.cpu_count() or 2) - 1))
    run(["make", "-C", str(src / "source"), "-j", jobs, "normal",
         f"YANEURAOU_EDITION={model['edition']}", f"TARGET_CPU={e['target_cpu']}", f"COMPILER={e['compiler']}"])

    built = src / "source" / BINARY_NAME
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(built, dest)
    (dest.parent / "build.json").write_text(json.dumps({
        "repo": e["repo"], "tag": e["tag"], "commit": head, "edition": model["edition"],
        "target_cpu": e["target_cpu"], "compiler": e["compiler"], "built_at": now(),
        "binary_sha256": sha256_file(dest),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not keep_src:
        shutil.rmtree(src, ignore_errors=True)
    print(f"[engine] ビルド完了: {dest}")
    return dest


# ------------------------------------------------------------------ model
def download(url: str, dest: Path) -> None:
    print(f"[model] ダウンロード: {url}", flush=True)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(url, timeout=60) as r, tmp.open("wb") as f:  # noqa: S310 (固定URL・ハッシュ照合あり)
        shutil.copyfileobj(r, f)
    tmp.replace(dest)


def extract_nn_bin(archive: Path, out: Path) -> None:
    with tempfile.TemporaryDirectory(dir=archive.parent) as td:
        if archive.suffix == ".7z":
            try:
                import py7zr
            except ImportError:
                raise SystemExit("py7zr がありません: .venv/bin/pip install -r requirements-analysis.txt")
            with py7zr.SevenZipFile(archive, "r") as z:
                z.extractall(td)
        else:
            shutil.unpack_archive(str(archive), td)
        found = sorted(Path(td).rglob("nn.bin"))
        if len(found) != 1:
            raise SystemExit(f"アーカイブ内の nn.bin が {len(found)} 個見つかりました: {[str(p) for p in found]}")
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(found[0], out)


def install_model(lock: dict, mid: str, model: dict) -> None:
    mdir = model_dir(mid)
    nn = mdir / "nn.bin"
    info_path = mdir / "install.json"
    if nn.exists() and info_path.exists():
        info = json.loads(info_path.read_text(encoding="utf-8"))
        if info.get("archive_sha256") == model["archive_sha256"] and sha256_file(nn) == info.get("nn_bin_sha256"):
            print(f"[model] 導入済み: {mid} ({model.get('display_name', mid)})")
            fill_lock_hash(mid, info["nn_bin_sha256"])
            return

    archive = engine_dir() / "downloads" / Path(model["url"]).name
    if not archive.exists() or sha256_file(archive) != model["archive_sha256"]:
        download(model["url"], archive)
    got = sha256_file(archive)
    if got != model["archive_sha256"]:
        archive.unlink(missing_ok=True)
        raise SystemExit(f"アーカイブのハッシュが一致しません（取得 {got} / lock {model['archive_sha256']}）。中止します")

    extract_nn_bin(archive, nn)
    nn_hash = sha256_file(nn)
    if model.get("nn_bin_sha256") and model["nn_bin_sha256"] != nn_hash:
        raise SystemExit(f"nn.bin のハッシュがロックと一致しません（{nn_hash} / {model['nn_bin_sha256']}）")
    info_path.write_text(json.dumps({
        "model_id": mid, "display_name": model.get("display_name", mid), "url": model["url"],
        "archive_sha256": got, "nn_bin_sha256": nn_hash, "installed_at": now(),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[model] 導入完了: {nn}（sha256 {nn_hash}）")
    fill_lock_hash(mid, nn_hash)


def fill_lock_hash(mid: str, nn_hash: str) -> None:
    """ロックの nn_bin_sha256 が空なら記入する（アーカイブのハッシュ照合済みの値）。"""
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    if lock["models"][mid].get("nn_bin_sha256"):
        return
    lock["models"][mid]["nn_bin_sha256"] = nn_hash
    LOCK_PATH.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[model] engine.lock.json に nn_bin_sha256 を記入しました。コミットしてください: {nn_hash}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", help="導入するモデル ID（既定: engine.lock.json の active_model）")
    ap.add_argument("--check", action="store_true", help="照合のみ")
    ap.add_argument("--keep-src", action="store_true", help="ビルド後もソースを残す")
    a = ap.parse_args()

    lock = load_lock()
    mid, model = get_model(lock, a.model)
    if not a.check:
        build_engine(lock, model, a.keep_src)
        install_model(lock, mid, model)
    try:
        info = resolve(mid)
    except EngineSetupError as e:
        print(f"NG: {e}")
        return 1
    print(f"OK: {info.model_name} [{info.model_id}] nn.bin sha256={info.nn_bin_sha256}\n    engine={info.binary}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
