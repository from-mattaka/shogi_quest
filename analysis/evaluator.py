"""評価値→期待勝率の変換と、悪手判定のロジック（エンジン・cshogi に依存しない純粋関数）。"""
from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Score:
    """手番側（または「自分」側）から見た評価値。cp か詰みのどちらか。"""
    cp: int | None = None
    mate: int | None = None      # 詰みまでの手数（絶対値。0 は「既に詰んでいる / 手数不明」）
    mate_win: bool = False       # mate のとき、こちら側が詰ませる側なら True

    @classmethod
    def mated(cls) -> "Score":
        """手番側が既に詰んでいる（合法手なし）。"""
        return cls(mate=0, mate_win=False)

    @property
    def is_mate(self) -> bool:
        return self.mate is not None

    @property
    def is_mate_win(self) -> bool:
        return self.mate is not None and self.mate_win

    @property
    def is_mate_loss(self) -> bool:
        return self.mate is not None and not self.mate_win

    def flip(self) -> "Score":
        if self.mate is not None:
            return Score(mate=self.mate, mate_win=not self.mate_win)
        return Score(cp=-(self.cp or 0))

    def winrate(self, scale: float = 600.0) -> float:
        if self.mate is not None:
            return 1.0 if self.mate_win else 0.0
        return 1.0 / (1.0 + math.exp(-(self.cp or 0) / scale))

    def fmt(self) -> str:
        """`+350` / `-80` / `#+5`（5手で詰ませる） / `#-3`（3手で詰まされる）。"""
        if self.mate is not None:
            sign = "+" if self.mate_win else "-"
            return f"#{sign}{self.mate}" if self.mate else f"#{sign}"
        return f"{self.cp:+d}"

    def fmt_ja(self) -> str:
        if self.mate is not None:
            if self.mate == 0:
                return "詰み（勝ち）" if self.mate_win else "詰まされ"
            return f"{self.mate}手詰め" if self.mate_win else f"{self.mate}手で詰まされる"
        return f"{self.cp:+d}"


@dataclass
class PVLine:
    multipv: int
    score: Score           # 手番側視点
    pv: list[str] = field(default_factory=list)
    depth: int = 0


@dataclass
class SearchResult:
    bestmove: str
    lines: list[PVLine]    # multipv 順

    @property
    def top(self) -> PVLine | None:
        return self.lines[0] if self.lines else None


@dataclass(frozen=True)
class Thresholds:
    dubious: float = 0.05
    mistake: float = 0.10
    blunder: float = 0.20

    @classmethod
    def from_config(cls, d: dict | None) -> "Thresholds":
        d = d or {}
        t = cls(**{k: float(v) for k, v in d.items() if k in ("dubious", "mistake", "blunder")})
        if not (0 < t.dubious <= t.mistake <= t.blunder):
            raise ValueError(f"thresholds は 0 < dubious <= mistake <= blunder にしてください: {t}")
        return t


def to_mine(score: Score, side_to_move: str, my_turn: str) -> Score:
    """手番側視点の評価値を自分視点に変換する。"""
    return score if side_to_move == my_turn else score.flip()


def missed_mate(before_mine: Score, after_mine: Score) -> bool:
    """着手前に自分から詰みがあったのに、着手後は詰みが無くなった。"""
    return before_mine.is_mate_win and not after_mine.is_mate_win


def winrate_drop(before_mine: Score, after_mine: Score, scale: float) -> float:
    return before_mine.winrate(scale) - after_mine.winrate(scale)


def is_candidate(before_mine: Score, after_mine: Score, move: str, best: str | None,
                 scale: float, th: Thresholds) -> bool:
    """第1パス: 深掘り（第2パス）の対象にするか。"""
    if missed_mate(before_mine, after_mine):
        return True
    if best is not None and move == best:
        return False
    return winrate_drop(before_mine, after_mine, scale) >= th.dubious


def classify(before_mine: Score, after_mine: Score, move: str, best: str | None,
             scale: float, th: Thresholds) -> str | None:
    """第2パス: 判定カテゴリを確定する。該当しなければ None。"""
    if missed_mate(before_mine, after_mine):
        return "詰み逃し"
    if best is not None and move == best:
        return None
    drop = winrate_drop(before_mine, after_mine, scale)
    if drop >= th.blunder:
        return "大悪手"
    if drop >= th.mistake:
        return "悪手"
    if drop >= th.dubious:
        return "疑問手"
    return None


def parse_info(line: str) -> tuple[PVLine, bool] | None:
    """USI の info 行から (PVLine, bound) を取り出す。score が無い行は None。"""
    t = line.split()
    if not t or t[0] != "info" or "score" not in t or "string" in t[:2]:
        return None
    multipv, depth, score, bound, pv = 1, 0, None, False, []
    i = 1
    while i < len(t):
        k = t[i]
        if k == "multipv":
            multipv = int(t[i + 1]); i += 2
        elif k == "depth":
            depth = int(t[i + 1]); i += 2
        elif k == "score":
            kind, val = t[i + 1], t[i + 2]
            if kind == "cp":
                score = Score(cp=int(val))
            elif kind == "mate":
                digits = val.lstrip("+-")
                score = Score(mate=int(digits) if digits else 0, mate_win=not val.startswith("-"))
            i += 3
        elif k in ("lowerbound", "upperbound"):
            bound = True; i += 1
        elif k == "pv":
            pv = t[i + 1:]; break
        elif k == "string":
            break
        else:
            i += 1
    if score is None:
        return None
    return PVLine(multipv=multipv, score=score, pv=pv, depth=depth), bound
