# 将棋クエスト対局記録 — qwalks

最終更新: 2026-11-28T04:16:06+09:00　/　総対局数: **158**　/　悪手検出済み: **132**

> 対局は GitHub Actions が毎日自動収集し、悪手検出（将棋AIによる解析）はローカルで手動実行しています。生データ: [`data/games_summary.csv`](data/games_summary.csv)　AI 相談用: [`AI_CONTEXT.md`](docs/ai/AI_CONTEXT.md)　悪手検出の説明: [`docs/mistake_analysis.md`](docs/mistake_analysis.md)

**[次の一手 問題集](https://from-mattaka.github.io/shogi_quest/quiz/)** — 悪手検出で見つかった局面をブラウザで解けます（GitHub Pages）

## 持ち時間別サマリー

| 持ち時間 | 対局数 | 勝 | 負 | 分 | 勝率 | 最新レート | 平均手数 |
|---|--:|--:|--:|--:|--:|--:|--:|
| 10分 | 2 | 2 | 0 | 0 | 100.0% | 1843 | 66.5 |
| 5分 | 156 | 79 | 77 | 0 | 50.6% | 1698 | 83.3 |
| 2分 | 0 | 0 | 0 | 0 | - | - | - |

勝率は引き分けを除いた `勝 / (勝 + 負)`。

## 直近20局

| 日時 | 持ち時間 | 手番 | 相手 | 結果 | 手数 | 終局理由 | 自レート | 棋譜 | 悪手検出 |
|---|---|---|---|:-:|--:|---|--:|---|---|
| 2026-11-28 03:39 | 5分 | ☖後 | 相手(1261) | ● 負 | 59 | 投了 | 1698 | [CSA](data/csa/shogi5/yrxiofujhj9g.csa) | - |
| 2026-11-28 03:29 | 5分 | ☗先 | 相手(1844) | ○ 勝 | 95 | 時間切れ | 1689 | [CSA](data/csa/shogi5/wv7xqb77e7lx.csa) | - |
| 2026-11-27 05:22 | 5分 | ☖後 | 相手(1904) | ● 負 | 125 | 時間切れ | 1692 | [CSA](data/csa/shogi5/ql7oz28chpmw.csa) | - |
| 2026-11-27 04:21 | 5分 | ☖後 | 相手(1443) | ○ 勝 | 74 | 切断 | 1690 | [CSA](data/csa/shogi5/tyjtvyp6kn1i.csa) | - |
| 2026-11-27 04:02 | 5分 | ☗先 | 相手(1736) | ● 負 | 116 | 時間切れ | 1695 | [CSA](data/csa/shogi5/nsj3f72udtlv.csa) | - |
| 2026-11-27 03:14 | 5分 | ☗先 | 相手(1751) | ○ 勝 | 133 | 詰み | 1694 | [CSA](data/csa/shogi5/rtpbx5lrk7bd.csa) | - |
| 2026-11-27 02:02 | 5分 | ☖後 | 相手(1777) | ○ 勝 | 58 | 投了 | 1687 | [CSA](data/csa/shogi5/aiy5q8qp8dv9.csa) | - |
| 2026-11-26 18:42 | 5分 | ☗先 | 相手(1746) | ● 負 | 84 | 投了 | 1692 | [CSA](data/csa/shogi5/w3x2c8b349f0.csa) | - |
| 2026-11-26 06:55 | 5分 | ☖後 | 相手(1678) | ○ 勝 | 46 | 投了 | 1685 | [CSA](data/csa/shogi5/ajd403we6ma6.csa) | - |
| 2026-11-26 06:52 | 5分 | ☗先 | 相手(1688) | ● 負 | 94 | 時間切れ | 1692 | [CSA](data/csa/shogi5/qj23zccgfd3b.csa) | - |
| 2026-11-26 03:46 | 5分 | ☖後 | 相手(1759) | ○ 勝 | 112 | 詰み | 1684 | [CSA](data/csa/shogi5/zqmwrysjgiwa.csa) | - |
| 2026-11-26 03:39 | 5分 | ☗先 | 相手(1609) | ● 負 | 14 | 投了 | 1690 | [CSA](data/csa/shogi5/h97se7qujisc.csa) | - |
| 2026-11-24 21:50 | 5分 | ☖後 | 相手(1656) | ○ 勝 | 134 | 詰み | 1685 | [CSA](data/csa/shogi5/5kztemm6oq7a.csa) | - |
| 2026-11-24 03:00 | 5分 | ☖後 | 相手(1900) | ● 負 | 131 | 時間切れ | 1688 | [CSA](data/csa/shogi5/39lbzoovwjug.csa) | - |
| 2026-11-23 18:56 | 5分 | ☗先 | 相手(1685) | ● 負 | 120 | 投了 | 1694 | [CSA](data/csa/shogi5/qj20jp0r8b98.csa) | - |
| 2026-11-23 14:10 | 5分 | ☗先 | 相手(1784) | ○ 勝 | 99 | 投了 | 1686 | [CSA](data/csa/shogi5/kjb7t2l93qek.csa) | - |
| 2026-11-21 12:33 | 5分 | ☖後 | 相手(1854) | ● 負 | 119 | 時間切れ | 1690 | [CSA](data/csa/shogi5/y3654poqv5nz.csa) | - |
| 2026-11-21 09:16 | 5分 | ☗先 | 相手(1726) | ○ 勝 | 43 | 切断 | 1683 | [CSA](data/csa/shogi5/nioko8fzmolr.csa) | - |
| 2026-11-21 07:07 | 5分 | ☗先 | 相手(1721) | ● 負 | 74 | 詰み | 1688 | [CSA](data/csa/shogi5/9dhyq4lzhmx3.csa) | - |
| 2026-11-21 06:58 | 5分 | ☖後 | 相手(1353) | ○ 勝 | 80 | 詰み | 1687 | [CSA](data/csa/shogi5/1w1ltd7ai2eu.csa) | - |

悪手検出の列: 評価関数名（レポートへのリンク）と、逃=詰み逃し・大=大悪手・悪=悪手・疑=疑問手 の件数。

## 悪手検出サマリー（評価関数・持ち時間別）

| 評価関数 | 持ち時間 | 解析局数 | 自分の手数 | 詰み逃し | 大悪手 | 悪手 | 疑問手 | 悪手率 | 1局あたり悪手 |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 水匠5 (`suisho5`) | 10分 | 2 | 67 | 0 | 2 | 2 | 7 | 6.0% | 2.00 |
| 水匠5 (`suisho5`) | 5分 | 130 | 5293 | 38 | 274 | 325 | 271 | 11.3% | 4.61 |

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
