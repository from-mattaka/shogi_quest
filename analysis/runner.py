"""1局分の2段階解析（第1パス: 全手スキャン → 第2パス: 悪手候補の深掘り）。"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field

from .engine import UsiEngine
from .evaluator import PVLine, Score, SearchResult, Thresholds, classify, is_candidate, to_mine, winrate_drop
from .kifu import Game
from .schema import CATEGORY_COUNT_COL

log = logging.getLogger("mistakes")


@dataclass
class Params:
    pass1_ms: int | None
    pass1_nodes: int | None
    pass2_ms: int | None
    pass2_nodes: int | None
    pass2_multipv: int
    threads: int
    hash_mb: int
    scale: float
    thresholds: Thresholds
    pv_moves: int
    skip_opening_plies: int
    analysis_version: int

    @staticmethod
    def _limit(ms, nodes) -> str:
        return f"nodes={nodes}" if nodes else f"movetime={ms}ms"

    @property
    def pass1_limit(self) -> str:
        return self._limit(self.pass1_ms, self.pass1_nodes)

    @property
    def pass2_limit(self) -> str:
        return self._limit(self.pass2_ms, self.pass2_nodes)


@dataclass
class Mistake:
    ply: int
    category: str
    before: Score            # 自分視点
    after: Score
    move_usi: str
    move_ja: str
    reply_pv_ja: str
    candidates: list[tuple[str, str, Score, str]]  # (usi, 日本語, 自分視点評価値, 読み筋日本語)
    sfen_before: str
    bod_before: str


@dataclass
class GameAnalysis:
    my_turn: str
    evals: list[Score]                     # 局面 k の評価値（自分視点, 第1パス）
    best: list[str | None]                 # 局面 k の第1パス最善手
    candidates: list[int] = field(default_factory=list)   # 深掘りした手数
    mistakes: list[Mistake] = field(default_factory=list)
    elapsed: float = 0.0

    def my_plies(self, game: Game) -> list[int]:
        return [k + 1 for k in range(game.n) if game.turns[k] == self.my_turn]


def _search(engine: UsiEngine, game: Game, k: int, multipv: int, ms, nodes) -> SearchResult:
    if game.terminal[k]:
        return SearchResult("resign", [PVLine(1, Score.mated(), [])])
    return engine.search(game.start_sfen, game.moves[:k], multipv, movetime_ms=ms, nodes=nodes)


def analyze_game(engine: UsiEngine, game: Game, my_turn: str, p: Params) -> GameAnalysis:
    t0 = time.monotonic()
    engine.new_game()

    # ---- 第1パス: 全局面を 1 回ずつ評価（局面 k の評価 = k 手目の事後評価 = k+1 手目の事前評価）
    evals: list[Score] = []
    best: list[str | None] = []
    for k in range(game.n + 1):
        r = _search(engine, game, k, 1, p.pass1_ms, p.pass1_nodes)
        top = r.top
        evals.append(to_mine(top.score if top else Score(cp=0), game.turns[k], my_turn))
        best.append(None if r.bestmove in ("resign", "win") else r.bestmove)
    ga = GameAnalysis(my_turn=my_turn, evals=evals, best=best)

    for ply in ga.my_plies(game):
        k = ply - 1
        if ply <= p.skip_opening_plies:
            continue
        if is_candidate(evals[k], evals[k + 1], game.moves[k], best[k], p.scale, p.thresholds):
            ga.candidates.append(ply)
    log.info("  第1パス完了: %d 局面, 深掘り候補 %d 手 (%.1fs)", game.n + 1, len(ga.candidates), time.monotonic() - t0)

    # ---- 第2パス: 候補局面だけ長めに MultiPV で再探索して判定を確定
    for ply in ga.candidates:
        k = ply - 1
        rb = _search(engine, game, k, p.pass2_multipv, p.pass2_ms, p.pass2_nodes)
        ra = _search(engine, game, k + 1, 1, p.pass2_ms, p.pass2_nodes)
        if not rb.top or not ra.top:
            continue
        before = to_mine(rb.top.score, game.turns[k], my_turn)
        after = to_mine(ra.top.score, game.turns[k + 1], my_turn)
        best2 = rb.top.pv[0] if rb.top.pv else (None if rb.bestmove in ("resign", "win") else rb.bestmove)
        cat = classify(before, after, game.moves[k], best2, p.scale, p.thresholds)
        log.info("  %3d手目 %s: 第2パス %s→%s (%+.1fpt) %s", ply, game.moves_ja[k], before.fmt(), after.fmt(),
                 -winrate_drop(before, after, p.scale) * 100, cat or "（該当なし）")
        if not cat:
            continue
        cands = []
        for line in rb.lines[: p.pass2_multipv]:
            if not line.pv:
                continue
            cands.append((line.pv[0], game.move_ja_at(k, line.pv[0]),
                          to_mine(line.score, game.turns[k], my_turn), game.pv_ja(k, line.pv, p.pv_moves)))
        ga.mistakes.append(Mistake(
            ply=ply, category=cat, before=before, after=after,
            move_usi=game.moves[k], move_ja=game.moves_ja[k],
            reply_pv_ja=game.pv_ja(k + 1, ra.top.pv, p.pv_moves) if not game.terminal[k + 1] else "",
            candidates=cands, sfen_before=game.sfens[k], bod_before=game.bods[k],
        ))
    ga.elapsed = time.monotonic() - t0
    return ga


def summary_counts(ga: GameAnalysis) -> dict[str, int]:
    c = {col: 0 for col in CATEGORY_COUNT_COL.values()}
    for m in ga.mistakes:
        c[CATEGORY_COUNT_COL[m.category]] += 1
    return c

