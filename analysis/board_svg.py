"""SFEN から将棋ソフト風の盤面図（SVG）を作る。外部ライブラリ・外部通信なし（cshogi で SFEN を読むだけ）。

Markdown レポートには `![…](img/xxx.svg)` で埋め込む。GitHub でも VS Code のプレビューでも表示できる。
- 駒は五角形の駒形＋漢字。相手の駒は 180 度回転、成駒は赤字。
- 直前の相手の指し手のマスを黄色で塗る。
- 矢印: 赤＝実戦の指し手、青＝AI の推奨手。打つ手は持ち駒の位置から矢印を引く。
- flip=True で後手から見た向き（自分が後手の局面を自分側から見る）。
"""
from __future__ import annotations

from html import escape
from pathlib import Path

import cshogi

from .kifu import KANJI_NUM

CELL = 40
BOARD = CELL * 9
TOP = 26                 # 筋の数字の分
HAND_W = 54              # 持ち駒の列の幅
GAP = 10
LEFT = HAND_W + GAP      # 盤の左端
RIGHT_LABEL = 22         # 段の漢数字の分
WIDTH = LEFT + BOARD + RIGHT_LABEL + GAP + HAND_W + 2
CAPTION_H = 30

PIECE_CHAR = {
    cshogi.PAWN: "歩", cshogi.LANCE: "香", cshogi.KNIGHT: "桂", cshogi.SILVER: "銀",
    cshogi.GOLD: "金", cshogi.BISHOP: "角", cshogi.ROOK: "飛", cshogi.KING: "玉",
    cshogi.PROM_PAWN: "と", cshogi.PROM_LANCE: "杏", cshogi.PROM_KNIGHT: "圭",
    cshogi.PROM_SILVER: "全", cshogi.PROM_BISHOP: "馬", cshogi.PROM_ROOK: "龍",
}
PROMOTED = {cshogi.PROM_PAWN, cshogi.PROM_LANCE, cshogi.PROM_KNIGHT, cshogi.PROM_SILVER,
            cshogi.PROM_BISHOP, cshogi.PROM_ROOK}
# pieces_in_hand の添字（歩=0 … 飛=6）と表示順（飛から）
HAND_ORDER = [(6, "飛"), (5, "角"), (4, "金"), (3, "銀"), (2, "桂"), (1, "香"), (0, "歩")]
DROP_IDX = {"R": 6, "B": 5, "G": 4, "S": 3, "N": 2, "L": 1, "P": 0}
FILES_JA = "１２３４５６７８９"
RANKS_JA = "一二三四五六七八九"

COLOR_PLAYED = "#d62728"
COLOR_BEST = "#1f6fd1"
FONT = "'Noto Serif JP','Noto Serif CJK JP','Hiragino Mincho ProN','Yu Mincho','YuMincho','MS Mincho',serif"
FONT_UI = "'Noto Sans JP','Noto Sans CJK JP','Hiragino Sans','Yu Gothic','Meiryo',sans-serif"


def _parse_sq(s: str) -> tuple[int, int]:
    """USI のマス（'7f'）→（筋 1-9, 段 0-8）。"""
    return int(s[0]), ord(s[1]) - ord("a")


class _Layout:
    def __init__(self, flip: bool):
        self.flip = flip

    def cell(self, file: int, rank: int) -> tuple[float, float]:
        """マスの左上座標。"""
        col = (file - 1) if self.flip else (9 - file)
        row = (8 - rank) if self.flip else rank
        return LEFT + col * CELL, TOP + row * CELL

    def center(self, file: int, rank: int) -> tuple[float, float]:
        x, y = self.cell(file, rank)
        return x + CELL // 2, y + CELL // 2


def _piece(cx: float, cy: float, ch: str, upright: bool, red: bool, size: float = 1.0) -> str:
    """駒 1 枚。駒形は <defs> の #k を使い回す（ファイルを小さくするため）。"""
    tf = f"translate({cx:g},{cy:g})" + ("" if upright else " rotate(180)") + (f" scale({size:g})" if size != 1 else "")
    cls = "p r" if red else "p"
    return f'<g transform="{tf}"><use href="#k"/><text class="{cls}" y="7">{escape(ch)}</text></g>'


def _arrow(x1: float, y1: float, x2: float, y2: float, color: str, mid: str) -> str:
    # 動かす駒の字が隠れないよう始点を少しずらし、矢じりはマスの中心の少し手前で止める
    dx, dy = x2 - x1, y2 - y1
    d = max((dx * dx + dy * dy) ** 0.5, 1)
    x1, y1 = x1 + dx / d * 14, y1 + dy / d * 14
    x2s, y2s = x2 - dx / d * 8, y2 - dy / d * 8
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2s:.1f}" y2="{y2s:.1f}" stroke="{color}" '
            f'stroke-width="5" stroke-linecap="round" opacity="0.72" marker-end="url(#{mid})"/>')


def sfen_to_svg(sfen: str, *, played: str | None = None, best: str | None = None,
                last: str | None = None, flip: bool = False, caption: str | None = None) -> str:
    """盤面図の SVG 文字列を返す。

    played / best / last は USI の指し手（'7g7f', 'P*5e'）。played=赤矢印、best=青矢印、last=黄色のマス。
    """
    b = cshogi.Board(sfen)
    L = _Layout(flip)
    height = TOP + BOARD + 8 + (CAPTION_H if caption else 0)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" font-family="{FONT_UI}">',
        "<style>"
        f".p{{font-family:{FONT};font-size:21px;font-weight:bold;text-anchor:middle;fill:#111}}.r{{fill:#b00000}}"
        ".c{font-size:14px;fill:#333;text-anchor:middle}"
        "</style>",
        "<defs>",
        '<polygon id="k" points="0,-17 11,-13 15,17 -15,17 -11,-13" fill="#f7dfa4" stroke="#7a5a2a" stroke-width="1"/>',
        *(f'<marker id="{mid}" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="3.2" markerHeight="3.2" '
          f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>'
          for mid, c in (("ah-played", COLOR_PLAYED), ("ah-best", COLOR_BEST))),
        "</defs>",
        f'<rect width="{WIDTH}" height="{height}" fill="#ffffff"/>',
        f'<rect x="{LEFT}" y="{TOP}" width="{BOARD}" height="{BOARD}" fill="#eac677" stroke="#3b2a12" stroke-width="2"/>',
    ]

    # 直前の指し手のマス
    if last and len(last) >= 4:
        f, r = _parse_sq(last[2:4])
        x, y = L.cell(f, r)
        out.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" fill="#ffe36e" opacity="0.85"/>')

    # 罫線・星
    grid = "".join(f"M{LEFT + i * CELL},{TOP}v{BOARD}M{LEFT},{TOP + i * CELL}h{BOARD}" for i in range(1, 9))
    out.append(f'<path d="{grid}" stroke="#3b2a12" stroke-width="0.8"/>')
    for i in (3, 6):
        for j in (3, 6):
            out.append(f'<circle cx="{LEFT + i * CELL}" cy="{TOP + j * CELL}" r="2.6" fill="#3b2a12"/>')

    # 座標
    for col in range(9):
        file = (col + 1) if flip else (9 - col)
        out.append(f'<text class="c" x="{LEFT + col * CELL + CELL // 2}" y="{TOP - 8}">{FILES_JA[file - 1]}</text>')
    for row in range(9):
        rank = (8 - row) if flip else row
        out.append(f'<text class="c" x="{LEFT + BOARD + RIGHT_LABEL // 2 + 1}" y="{TOP + row * CELL + CELL // 2 + 5}">{RANKS_JA[rank]}</text>')

    # 盤上の駒
    viewer = cshogi.WHITE if flip else cshogi.BLACK
    for file in range(1, 10):
        for rank in range(9):
            p = b.piece((file - 1) * 9 + rank)
            if not p:
                continue
            pt, owner = p % 16, (cshogi.WHITE if p >= 16 else cshogi.BLACK)
            ch = PIECE_CHAR[pt]
            if pt == cshogi.KING and owner == cshogi.WHITE:
                ch = "王"
            cx, cy = L.center(file, rank)
            out.append(_piece(cx, cy, ch, owner == viewer, pt in PROMOTED))

    # 持ち駒（手前側＝右下、奥側＝左上）。打つ手の矢印の始点もここで決める
    hand_pos: dict[tuple[int, int], tuple[float, float]] = {}
    hands = b.pieces_in_hand
    for color in (cshogi.BLACK, cshogi.WHITE):
        near = color == viewer
        x = LEFT + BOARD + RIGHT_LABEL + GAP + HAND_W // 2 if near else HAND_W // 2
        mark = "☗" if color == cshogi.BLACK else "☖"
        name = "先手" if color == cshogi.BLACK else "後手"
        turn = b.turn == color
        items = [(idx, ch, hands[color][idx]) for idx, ch in HAND_ORDER if hands[color][idx]]
        step = 38
        block = 44 + max(len(items), 1) * step
        y0 = TOP + BOARD - block if near else TOP
        bg = "#fff4d6" if turn else "#f4f4f4"
        out.append(f'<rect x="{x - HAND_W // 2}" y="{y0}" width="{HAND_W}" height="{block}" rx="5" fill="{bg}" '
                   f'stroke="{"#c9902b" if turn else "#cccccc"}" stroke-width="{2 if turn else 1}"/>')
        out.append(f'<text x="{x}" y="{y0 + 18}" font-size="15" text-anchor="middle" fill="#222">{mark}</text>')
        out.append(f'<text x="{x}" y="{y0 + 35}" font-size="11" text-anchor="middle" fill="#444">{name}</text>')
        if not items:
            out.append(f'<text x="{x}" y="{y0 + 44 + step / 2 + 4}" font-size="11" text-anchor="middle" fill="#888">なし</text>')
        for i, (idx, ch, n) in enumerate(items):
            cy = y0 + 44 + i * step + step / 2
            out.append(_piece(x - 7, cy, ch, True, False, size=0.85))
            if n > 1:
                out.append(f'<text x="{x + 16}" y="{cy + 14}" font-size="12" font-weight="bold" '
                           f'text-anchor="middle" fill="#222">{escape(KANJI_NUM[n] if n < len(KANJI_NUM) else str(n))}</text>')
            hand_pos[(color, idx)] = (x - 7, cy)

    # 矢印（青＝AI を下、赤＝実戦を上に重ねる）
    for usi, color, mid in ((best, COLOR_BEST, "ah-best"), (played, COLOR_PLAYED, "ah-played")):
        if not usi or len(usi) < 4:
            continue
        tx, ty = L.center(*_parse_sq(usi[2:4]))
        if usi[1] == "*":
            start = hand_pos.get((b.turn, DROP_IDX.get(usi[0], -1)))
            if not start:
                continue
            fx, fy = start
        else:
            fx, fy = L.center(*_parse_sq(usi[0:2]))
        out.append(_arrow(fx, fy, tx, ty, color, mid))

    if caption:
        out.append(f'<text x="{LEFT + BOARD // 2}" y="{TOP + BOARD + 8 + 20}" font-size="14" text-anchor="middle" '
                   f'fill="#222">{escape(caption)}</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def position_svg(sfen: str, ply: int, *, played: str | None, best: str | None,
                 last: str | None, my_turn: str) -> str:
    """自分の手番の局面を、自分側から見た向きで描く（my_turn は SENTE / GOTE）。"""
    flip = my_turn == "GOTE"
    side = "☖後手番" if " w " in sfen else "☗先手番"
    caption = f"{ply}手目の局面（{side}）" + ("　※後手側から見た図" if flip else "")
    return sfen_to_svg(sfen, played=played, best=best, last=last, flip=flip, caption=caption)


def write_images(base: Path, images: dict[str, str], stale_glob: str | None = None) -> None:
    """images {base からの相対パス: SVG} を書き出す。stale_glob に合う古い画像は先に消す。"""
    if stale_glob:
        for old in base.glob(stale_glob):
            old.unlink()
    for rel, svg in images.items():
        path = base / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(svg, encoding="utf-8", newline="\n")


def legend(played_ja: str | None, best_ja: str | None) -> str:
    """Markdown 用の凡例（盤面図の下に置く）。"""
    parts = []
    if played_ja:
        parts.append(f"🔴 実戦 {played_ja}")
    if best_ja:
        parts.append(f"🔵 AI推奨 {best_ja}")
    parts.append("🟨 直前の相手の指し手")
    return "　".join(parts)


def markdown_block(img_rel: str, alt: str, bod: str, played_ja: str | None = None,
                   best_ja: str | None = None) -> list[str]:
    """画像＋凡例＋折りたたんだテキスト盤面図（BOD。将棋ソフトに貼り付けられる）の Markdown 行。"""
    return [
        f"![{alt}]({img_rel})",
        "",
        legend(played_ja, best_ja),
        "",
        "<details><summary>テキストの盤面図（BOD・将棋ソフトに貼り付け可）</summary>",
        "",
        "```text",
        bod,
        "```",
        "",
        "</details>",
    ]
