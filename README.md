# 将棋クエスト対局記録 — qwalks

最終更新: 2026-11-18T03:52:38+09:00　/　総対局数: **116**　/　悪手検出済み: **89**

> 対局は GitHub Actions が毎日自動収集し、悪手検出（将棋AIによる解析）はローカルで手動実行しています。生データ: [`data/games_summary.csv`](data/games_summary.csv)　AI 相談用: [`AI_CONTEXT.md`](docs/ai/AI_CONTEXT.md)　悪手検出の説明: [`docs/mistake_analysis.md`](docs/mistake_analysis.md)

**[次の一手 問題集](https://from-mattaka.github.io/shogi_quest/quiz/)** — 悪手検出で見つかった局面をブラウザで解けます（GitHub Pages）

## 持ち時間別サマリー

| 持ち時間 | 対局数 | 勝 | 負 | 分 | 勝率 | 最新レート | 平均手数 |
|---|--:|--:|--:|--:|--:|--:|--:|
| 10分 | 2 | 2 | 0 | 0 | 100.0% | 1843 | 66.5 |
| 5分 | 114 | 55 | 59 | 0 | 48.2% | 1668 | 81.3 |
| 2分 | 0 | 0 | 0 | 0 | - | - | - |

勝率は引き分けを除いた `勝 / (勝 + 負)`。

## 直近20局

| 日時 | 持ち時間 | 手番 | 相手 | 結果 | 手数 | 終局理由 | 自レート | 棋譜 | 悪手検出 |
|---|---|---|---|:-:|--:|---|--:|---|---|
| 2026-11-18 01:12 | 5分 | ☗先 | 相手(1539) | ○ 勝 | 83 | 詰み | 1668 | [CSA](data/csa/shogi5/lmxlq3gzlo1k.csa) | - |
| 2026-11-18 00:59 | 5分 | ☖後 | 相手(1856) | ○ 勝 | 86 | 投了 | 1659 | [CSA](data/csa/shogi5/gfyvc296cxem.csa) | - |
| 2026-11-18 00:52 | 5分 | ☗先 | 相手(1606) | ○ 勝 | 99 | 時間切れ | 1654 | [CSA](data/csa/shogi5/zw2iwppueqwf.csa) | - |
| 2026-11-17 04:08 | 5分 | ☖後 | 相手(1692) | ● 負 | 105 | 時間切れ | 1660 | [CSA](data/csa/shogi5/1d2x4flmctj7.csa) | - |
| 2026-11-17 03:59 | 5分 | ☗先 | 相手(1562) | ● 負 | 66 | 投了 | 1667 | [CSA](data/csa/shogi5/c320vrfsxsa5.csa) | - |
| 2026-11-17 03:32 | 5分 | ☖後 | 相手(1371) | ○ 勝 | 112 | 詰み | 1667 | [CSA](data/csa/shogi5/rptz2tfjacoi.csa) | - |
| 2026-11-17 03:07 | 5分 | ☗先 | 相手(1454) | ● 負 | 96 | 時間切れ | 1676 | [CSA](data/csa/shogi5/aaa5ebeiiird.csa) | - |
| 2026-11-17 02:38 | 5分 | ☖後 | 相手(1341) | ○ 勝 | 36 | 投了 | 1675 | [CSA](data/csa/shogi5/c99nz039fot8.csa) | - |
| 2026-11-17 02:33 | 5分 | ☗先 | 相手(1527) | ○ 勝 | 91 | 投了 | 1674 | [CSA](data/csa/shogi5/u5257tm4vzef.csa) | - |
| 2026-11-16 21:07 | 5分 | ☖後 | 相手(1741) | ● 負 | 61 | 投了 | 1679 | [CSA](data/csa/shogi5/yj0fhzepxh3g.csa) | - |
| 2026-11-16 20:52 | 5分 | ☗先 | 相手(1669) | ○ 勝 | 71 | 時間切れ | 1673 | [CSA](data/csa/shogi5/ft98xnite99i.csa) | - |
| 2026-11-16 20:29 | 5分 | ☖後 | 相手(1872) | ○ 勝 | 68 | 詰み | 1664 | [CSA](data/csa/shogi5/aau7l0m9df11.csa) | - |
| 2026-11-16 20:18 | 5分 | ☗先 | 相手(1687) | ○ 勝 | 39 | 投了 | 1657 | [CSA](data/csa/shogi5/wtzekthsq676.csa) | - |
| 2026-11-16 20:12 | 5分 | ☖後 | 相手(1588) | ○ 勝 | 60 | 投了 | 1652 | [CSA](data/csa/shogi5/olz4qltehr45.csa) | - |
| 2026-11-16 01:56 | 5分 | ☗先 | 相手(2085) | ● 負 | 86 | 詰み | 1653 | [CSA](data/csa/shogi5/m1joexmbyxjs.csa) | - |
| 2026-11-16 01:47 | 5分 | ☖後 | 相手(1635) | ○ 勝 | 16 | 投了 | 1649 | [CSA](data/csa/shogi5/gpbd1plec803.csa) | - |
| 2026-11-15 00:42 | 5分 | ☗先 | 相手(1663) | ○ 勝 | 83 | 詰み | 1642 | [CSA](data/csa/shogi5/hm9k1flvfmqf.csa) | - |
| 2026-11-14 19:02 | 5分 | ☗先 | 相手(1593) | ● 負 | 94 | 詰み | 1649 | [CSA](data/csa/shogi5/dfl6vvybuzqw.csa) | - |
| 2026-11-14 18:50 | 5分 | ☖後 | 相手(1619) | ○ 勝 | 98 | 詰み | 1644 | [CSA](data/csa/shogi5/o402dz30yh03.csa) | - |
| 2026-11-14 18:42 | 5分 | ☖後 | 相手(1706) | ● 負 | 75 | 詰み | 1645 | [CSA](data/csa/shogi5/3ll02cic5ptm.csa) | - |

悪手検出の列: 評価関数名（レポートへのリンク）と、逃=詰み逃し・大=大悪手・悪=悪手・疑=疑問手 の件数。

## 悪手検出サマリー（評価関数・持ち時間別）

| 評価関数 | 持ち時間 | 解析局数 | 自分の手数 | 詰み逃し | 大悪手 | 悪手 | 疑問手 | 悪手率 | 1局あたり悪手 |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 水匠5 (`suisho5`) | 10分 | 2 | 67 | 0 | 2 | 2 | 7 | 6.0% | 2.00 |
| 水匠5 (`suisho5`) | 5分 | 87 | 3572 | 28 | 195 | 229 | 189 | 11.9% | 4.87 |

悪手率 = (大悪手 + 悪手) / 自分の手数。一覧: [`data/analysis/mistakes.csv`](data/analysis/mistakes.csv)

## ローカルでの分析手順（定期的に手動で実行）

対局の収集は Actions が自動で行います。分析は次の順にローカルで実行します（初回セットアップは [`docs/mistake_analysis.md`](docs/mistake_analysis.md) の「初回セットアップ」）。
2・3 は 1 の結果（`data/analysis/`）を読むだけなので、必ず 1 の後に実行します。

```bash
git pull                                         # 0. Actions が収集した対局を取り込む
.venv/bin/python analyze_mistakes.py             # 1. 局面の解析（悪手検出。未解析の対局だけ。1局30〜60秒）
.venv/bin/python make_quiz.py                    # 2. 悪手の問題集（quiz/index.html）を作り直す
.venv/bin/python analyze_opening_study.py        # 3. 序盤の同一局面での悪手の分析（data/analysis/study/）
git add data/analysis quiz README.md docs/ai/AI_CONTEXT.md
git commit -m "analysis: ..." && git push
```

| 手順 | 内容 | 説明 |
|---|---|---|
| 1. `analyze_mistakes.py` | 将棋AIで対局を解析し、レポート・`mistakes.csv`・README を更新 | [`docs/mistake_analysis.md`](docs/mistake_analysis.md) |
| 2. `make_quiz.py` | `mistakes.csv` から次の一手問題集を作る（エンジン不要・数秒） | [`docs/mistake_analysis.md`](docs/mistake_analysis.md) の「次の一手問題集」 |
| 3. `analyze_opening_study.py` | 序盤に繰り返し出た同じ局面での悪手をまとめる（エンジン不要・数秒） | [`docs/opening_study.md`](docs/opening_study.md) |

- 解析対象の確認だけなら `analyze_mistakes.py --dry-run`。途中で Ctrl+C しても、次回は続きから再開します
- push で README が競合したら `analyze_mistakes.py --regen-only` で作り直します
