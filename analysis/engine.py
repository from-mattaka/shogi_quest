"""USI エンジン（やねうら王）のラッパー。"""
from __future__ import annotations

import logging
import queue
import subprocess
import threading
import time
from pathlib import Path

from .evaluator import PVLine, Score, SearchResult, parse_info

log = logging.getLogger("engine")


class EngineError(RuntimeError):
    pass


class UsiEngine:
    def __init__(self, binary: Path):
        self.binary = Path(binary)
        self.proc = subprocess.Popen(
            [str(self.binary)], cwd=str(self.binary.parent),
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace", bufsize=1,
        )
        self._q: queue.Queue[str | None] = queue.Queue()
        threading.Thread(target=self._reader, daemon=True).start()
        self.name = ""
        self.options: set[str] = set()
        self._multipv = None

    # ---------------------------------------------------------- 低レベル
    def _reader(self) -> None:
        assert self.proc.stdout
        for line in self.proc.stdout:
            self._q.put(line.rstrip("\n"))
        self._q.put(None)

    def send(self, cmd: str) -> None:
        log.debug("> %s", cmd)
        assert self.proc.stdin
        self.proc.stdin.write(cmd + "\n")
        self.proc.stdin.flush()

    def _readline(self, deadline: float) -> str:
        try:
            line = self._q.get(timeout=max(0.01, deadline - time.monotonic()))
        except queue.Empty:
            raise EngineError("エンジンの応答がタイムアウトしました") from None
        if line is None:
            raise EngineError(f"エンジンが終了しました（終了コード {self.proc.poll()}）")
        log.debug("< %s", line)
        return line

    # ---------------------------------------------------------- 手順
    def handshake(self, timeout: float = 30) -> None:
        self.send("usi")
        deadline = time.monotonic() + timeout
        while True:
            line = self._readline(deadline)
            if line.startswith("id name "):
                self.name = line[len("id name "):].strip()
            elif line.startswith("option name "):
                self.options.add(line.split()[2])
            elif line == "usiok":
                return

    def set_option(self, name: str, value) -> bool:
        if name not in self.options:
            log.debug("option %s はこのエンジンに無いので設定しません", name)
            return False
        if isinstance(value, bool):
            value = "true" if value else "false"
        self.send(f"setoption name {name} value {value}")
        if name == "MultiPV":
            self._multipv = int(value)
        return True

    def isready(self, timeout: float = 180) -> None:
        self.send("isready")
        deadline = time.monotonic() + timeout
        while True:
            line = self._readline(deadline)
            if line == "readyok":
                return
            if "Error" in line or "error" in line:
                log.warning("engine: %s", line)

    def configure(self, eval_dir: Path, threads: int, hash_mb: int) -> None:
        self.handshake()
        for k, v in {
            "Threads": threads,
            "USI_Hash": hash_mb,
            "Hash": hash_mb,
            "EvalDir": str(eval_dir),
            "EvalFile": "nn.bin",
            "BookFile": "no_book",
            "USI_OwnBook": False,
            "NetworkDelay": 0,
            "NetworkDelay2": 0,
            "MinimumThinkingTime": 0,
            "ConsiderationMode": True,    # 読み筋を省略せずに出す
            "OutputFailLHPV": False,
            "PvInterval": 0,
            "ResignValue": 99999,
            "MaxMovesToDraw": 0,
            "USI_Ponder": False,
            "Stochastic_Ponder": False,
            "MultiPV": 1,
        }.items():
            self.set_option(k, v)
        self.isready()

    def new_game(self) -> None:
        self.send("usinewgame")

    def search(self, start_sfen: str, moves: list[str], multipv: int,
               movetime_ms: int | None = None, nodes: int | None = None) -> SearchResult:
        if multipv != self._multipv:
            self.set_option("MultiPV", multipv)
        pos = f"position sfen {start_sfen}"
        if moves:
            pos += " moves " + " ".join(moves)
        self.send(pos)
        if nodes:
            self.send(f"go nodes {int(nodes)}")
            timeout = 600.0
        else:
            self.send(f"go movetime {int(movetime_ms or 1000)}")
            timeout = (movetime_ms or 1000) / 1000 * 3 + 30

        exact: dict[int, PVLine] = {}
        bounded: dict[int, PVLine] = {}
        deadline = time.monotonic() + timeout
        while True:
            line = self._readline(deadline)
            if line.startswith("info "):
                parsed = parse_info(line)
                if parsed:
                    pl, bound = parsed
                    (bounded if bound else exact)[pl.multipv] = pl
            elif line.startswith("bestmove"):
                t = line.split()
                best = t[1] if len(t) > 1 else "resign"
                ponder = t[3] if len(t) > 3 and t[2] == "ponder" else None
                break

        keys = sorted(set(exact) | set(bounded))
        lines = [exact.get(k) or bounded[k] for k in keys]
        if not lines:
            if best == "resign":
                lines = [PVLine(1, Score.mated(), [])]
            elif best == "win":
                lines = [PVLine(1, Score(mate=0, mate_win=True), [])]
        elif best not in ("resign", "win") and lines[0].pv and lines[0].pv[0] != best:
            # 最後の完了した反復の後で最善手が変わった（途中の反復で fail-high した）場合、
            # bestmove の手で始まる bound 付きの行を使う。無ければ bestmove + ponder だけにする
            alt = bounded.get(1)
            if alt and alt.pv and alt.pv[0] == best:
                lines[0] = alt
            else:
                lines[0] = PVLine(1, lines[0].score, [best] + ([ponder] if ponder else []), lines[0].depth)
        return SearchResult(bestmove=best, lines=lines)

    def quit(self) -> None:
        try:
            self.send("quit")
            self.proc.wait(timeout=10)
        except Exception:  # noqa: BLE001
            self.proc.kill()
