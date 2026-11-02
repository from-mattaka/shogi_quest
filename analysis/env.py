"""エンジン・評価関数の置き場所の解決と、使用モデルの照合（標準ライブラリのみ）。

配置（既定。環境変数 SHOGI_ENGINE_DIR で変更可）:
    .engine/bin/{tag}-{edition}-{cpu}-{compiler}/YaneuraOu-by-gcc   ← ビルド種別ごと
    .engine/eval/{model_id}/nn.bin                                  ← 評価関数ごと
    .engine/eval/{model_id}/install.json                            ← 取得元とハッシュの記録
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCK_PATH = ROOT / "engine" / "engine.lock.json"
BINARY_NAME = "YaneuraOu-by-gcc"


class EngineSetupError(RuntimeError):
    """エンジン・評価関数が未導入、またはロックファイルと一致しない。"""


def engine_dir() -> Path:
    return Path(os.environ.get("SHOGI_ENGINE_DIR") or ROOT / ".engine")


def load_lock() -> dict:
    return json.loads(LOCK_PATH.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_key(lock: dict, model: dict) -> str:
    e = lock["engine"]
    return f"{e['tag']}-{model['edition']}-{e['target_cpu']}-{e['compiler']}"


def binary_path(lock: dict, model: dict) -> Path:
    return engine_dir() / "bin" / build_key(lock, model) / BINARY_NAME


def model_dir(model_id: str) -> Path:
    return engine_dir() / "eval" / model_id


def get_model(lock: dict, model_id: str | None = None) -> tuple[str, dict]:
    mid = model_id or lock["active_model"]
    if mid not in lock["models"]:
        raise EngineSetupError(f"engine.lock.json の models に '{mid}' がありません（定義済み: {', '.join(lock['models'])}）")
    return mid, lock["models"][mid]


@dataclass
class EngineInfo:
    engine_tag: str          # 例: V9.00/YANEURAOU_ENGINE_NNUE/AVX2
    engine_commit: str
    binary: Path
    model_id: str
    model_name: str
    eval_dir: Path
    nn_bin_sha256: str
    archive_sha256: str
    engine_name: str = ""    # USI の id name（起動後に埋める）

    @property
    def label(self) -> str:
        """人が読む用の解析環境 ID。"""
        name = self.engine_name or "YaneuraOu"
        return f"{name} ({self.engine_tag}) / {self.model_name} [{self.model_id}] nn.bin sha256:{self.nn_bin_sha256[:12]}"


def resolve(model_id: str | None = None) -> EngineInfo:
    """ロックファイルの内容と実体を照合し、解析に使う環境を返す。不一致なら例外。"""
    lock = load_lock()
    mid, model = get_model(lock, model_id)
    hint = "`python engine/setup_engine.py` を実行してください（docs/engine_model.md）"

    binary = binary_path(lock, model)
    if not binary.exists():
        raise EngineSetupError(f"エンジンがビルドされていません: {binary}\n{hint}")

    mdir = model_dir(mid)
    nn = mdir / "nn.bin"
    info_path = mdir / "install.json"
    if not nn.exists() or not info_path.exists():
        raise EngineSetupError(f"評価関数 '{mid}' が導入されていません: {nn}\n{hint}")

    installed = json.loads(info_path.read_text(encoding="utf-8"))
    if installed.get("archive_sha256") != model["archive_sha256"]:
        raise EngineSetupError(
            f"評価関数 '{mid}' の導入元がロックファイルと一致しません"
            f"（導入済み {installed.get('archive_sha256', '?')[:12]} / lock {model['archive_sha256'][:12]}）\n{hint}"
        )

    actual = sha256_file(nn)
    expected = model.get("nn_bin_sha256") or installed.get("nn_bin_sha256")
    if expected and actual != expected:
        raise EngineSetupError(
            f"nn.bin のハッシュが一致しません（実体 {actual[:12]} / 期待 {expected[:12]}）。"
            f"ファイルが差し替えられた可能性があります。\n{hint}"
        )

    e = lock["engine"]
    return EngineInfo(
        engine_tag=f"{e['tag']}/{model['edition']}/{e['target_cpu']}",
        engine_commit=e.get("commit", ""),
        binary=binary,
        model_id=mid,
        model_name=model.get("display_name", mid),
        eval_dir=mdir,
        nn_bin_sha256=actual,
        archive_sha256=model["archive_sha256"],
    )
