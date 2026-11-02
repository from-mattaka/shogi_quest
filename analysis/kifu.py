"""CSA 棋譜の読み込みと、USI 指し手・SFEN・BOD 盤面図・日本語表記への変換（cshogi を使用）。"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import cshogi
from cshogi import CSA

FILES_JA = "１２３４５６７８９"
RANKS_JA = "一二三四五六七八九"
PIECE_JA = {
    cshogi.PAWN: "歩", cshogi.LANCE: "香", cshogi.KNIGHT: "桂", cshogi.SILVER: "銀",
    cshogi.GOLD: "金", cshogi.BISHOP: "角", cshogi.ROOK: "飛", cshogi.KING: "玉",
    cshogi.PROM_PAWN: "と", cshogi.PROM_LANCE: "成香", cshogi.PROM_KNIGHT: "成桂",
    cshogi.PROM_SILVER: "成銀", cshogi.PROM_BISHOP: "馬", cshogi.PROM_ROOK: "龍",
}
PROMOTABLE = {cshogi.PAWN, cshogi.LANCE, cshogi.KNIGHT, cshogi.SILVER, cshogi.BISHOP, cshogi.ROOK}
DROP_JA = {"P": "歩", "L": "香", "N": "桂", "S": "銀", "G": "金", "B": "角", "R": "飛"}
HAND_ORDER = [(6, "飛"), (5, "角"), (4, "金"), (3, "銀"), (2, "桂"), (1, "香"), (0, "歩")]  # pieces_in_hand の添字
KANJI_NUM = ["", "", "二", "三", "四", "五", "六", "七", "八", "九", "十",
             "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八"]


def turn_name(color: int) -> str:
    return "SENTE" if color == cshogi.BLACK else "GOTE"


def _sq(file: int, rank_idx: int) -> int:
    """筋(1-9)・段(0-8) → cshogi のマス番号（1一=0, 1二=1, …, 9九=80）。"""
    return (file - 1) * 9 + rank_idx


def _to_part(usi: str) -> str:
    return usi[2:4]


def move_to_ja(board: cshogi.Board, usi: str, prev_usi: str | None = None) -> str:
    """着手前の盤面と USI 指し手から `▲７六歩(77)` 形式の文字列を作る。"""
    mark = "▲" if board.turn == cshogi.BLACK else "△"
    to = _to_part(usi)
    to_file, to_rank = int(to[0]), ord(to[1]) - ord("a")
    if prev_usi and _to_part(prev_usi) == to:
        dest = "同"
    else:
        dest = FILES_JA[to_file - 1] + RANKS_JA[to_rank]

    if usi[1] == "*":
        return f"{mark}{dest}{DROP_JA[usi[0]]}打"

    fr_file, fr_rank = int(usi[0]), ord(usi[1]) - ord("a")
    pt = board.piece(_sq(fr_file, fr_rank)) % 16
    name = PIECE_JA.get(pt, "?")
    suffix = ""
    if usi.endswith("+"):
        suffix = "成"
    elif pt in PROMOTABLE:
        zone = (0, 1, 2) if board.turn == cshogi.BLACK else (6, 7, 8)
        if fr_rank in zone or to_rank in zone:
            suffix = "不成"
    return f"{mark}{dest}{name}{suffix}({fr_file}{fr_rank + 1})"


def pv_to_ja(sfen: str, pv: list[str], prev_usi: str | None, limit: int) -> str:
    """読み筋（USI 列）を日本語の空白区切りに変換。不正な手が来たらそこで打ち切る。"""
    b = cshogi.Board(sfen)
    out, prev = [], prev_usi
    for u in pv[:limit]:
        m = b.move_from_usi(u)
        if not m or not b.is_legal(m):
            break
        out.append(move_to_ja(b, u, prev))
        b.push(m)
        prev = u
    return " ".join(out)


def _hand_ja(counts) -> str:
    parts = []
    for idx, name in HAND_ORDER:
        n = counts[idx]
        if n:
            parts.append(name + (KANJI_NUM[n] if n > 1 else ""))
    return "　".join(parts) if parts else "なし"


def to_bod(board: cshogi.Board, ply: int, last_ja: str | None = None) -> str:
    """BOD（柿木形式の盤面図）。cshogi の to_bod があればそれを使う。"""
    if hasattr(board, "to_bod"):
        try:
            return board.to_bod().rstrip("\n")
        except Exception:  # noqa: BLE001 — 失敗時は自前実装
            pass
    black, white = board.pieces_in_hand
    rows = ["後手の持駒：" + _hand_ja(white), "  ９ ８ ７ ６ ５ ４ ３ ２ １", "+---------------------------+"]
    for r in range(9):
        cells = []
        for f in range(9, 0, -1):
            p = board.piece(_sq(f, r))
            if p == 0:
                cells.append(" ・")
            else:
                name = PIECE_JA[p % 16]
                name = {"成香": "杏", "成桂": "圭", "成銀": "全"}.get(name, name)
                cells.append(("v" if p >= 16 else " ") + name)
        rows.append("|" + "".join(cells) + "|" + RANKS_JA[r])
    rows += ["+---------------------------+", "先手の持駒：" + _hand_ja(black), f"手数＝{ply}"]
    if last_ja:
        rows[-1] += f"  {last_ja}  まで"
    if board.turn == cshogi.WHITE:
        rows.append("後手番")
    return "\n".join(rows)


@dataclass
class Game:
    start_sfen: str
    moves: list[str]                                   # USI
    sfens: list[str] = field(default_factory=list)     # 各局面（0..N）
    turns: list[str] = field(default_factory=list)     # 各局面の手番 SENTE/GOTE
    terminal: list[bool] = field(default_factory=list) # 合法手なし（詰み）か
    moves_ja: list[str] = field(default_factory=list)  # moves_ja[i] = i+1 手目
    bods: list[str] = field(default_factory=list)

    @property
    def n(self) -> int:
        return len(self.moves)

    def pv_ja(self, k: int, pv: list[str], limit: int) -> str:
        """局面 k からの読み筋を日本語に（直前の手 = k 手目を「同」の判定に使う）。"""
        return pv_to_ja(self.sfens[k], pv, self.moves[k - 1] if k > 0 else None, limit)

    def move_ja_at(self, k: int, usi: str) -> str:
        return pv_to_ja(self.sfens[k], [usi], self.moves[k - 1] if k > 0 else None, 1) or usi


def _parse_moves(text: str) -> tuple[str, list[str]]:
    try:
        parsers = CSA.Parser.parse_str(text)
        p = parsers[0]
        return p.sfen, [cshogi.move_to_usi(m) for m in p.moves]
    except Exception:  # noqa: BLE001 — 予備: 平手前提で 1 手ずつ読む
        b = cshogi.Board()
        start = b.sfen()
        moves = []
        for line in text.splitlines():
            s = line.strip()
            if len(s) >= 7 and s[0] in "+-" and s[1:5].isdigit():
                m = b.move_from_csa(s[1:7])
                moves.append(cshogi.move_to_usi(m))
                b.push(m)
        return start, moves


def load_game(path: Path) -> Game:
    start, moves = _parse_moves(Path(path).read_text(encoding="utf-8"))
    g = Game(start_sfen=start, moves=moves)
    b = cshogi.Board(start)
    prev = None
    for k in range(len(moves) + 1):
        g.sfens.append(b.sfen())
        g.turns.append(turn_name(b.turn))
        g.terminal.append(b.is_game_over())
        g.bods.append(to_bod(b, k, g.moves_ja[-1] if g.moves_ja else None))
        if k == len(moves):
            break
        u = moves[k]
        m = b.move_from_usi(u)
        if not m or not b.is_legal(m):
            raise ValueError(f"{path}: {k + 1}手目 {u} が不正です")
        g.moves_ja.append(move_to_ja(b, u, prev))
        b.push(m)
        prev = u
    return g
