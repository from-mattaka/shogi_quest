# 将棋クエスト対局記録 — qwalks

最終更新: 2026-11-22T02:00:53+09:00　/　総対局数: **142**　/　悪手検出済み: **132**

> 対局は GitHub Actions が毎日自動収集し、悪手検出（将棋AIによる解析）はローカルで手動実行しています。生データ: [`data/games_summary.csv`](data/games_summary.csv)　AI 相談用: [`AI_CONTEXT.md`](docs/ai/AI_CONTEXT.md)　悪手検出の説明: [`docs/mistake_analysis.md`](docs/mistake_analysis.md)

**[次の一手 問題集](https://from-mattaka.github.io/shogi_quest/quiz/)** — 悪手検出で見つかった局面をブラウザで解けます（GitHub Pages）

## 持ち時間別サマリー

| 持ち時間 | 対局数 | 勝 | 負 | 分 | 勝率 | 最新レート | 平均手数 |
|---|--:|--:|--:|--:|--:|--:|--:|
| 10分 | 2 | 2 | 0 | 0 | 100.0% | 1843 | 66.5 |
| 5分 | 140 | 71 | 69 | 0 | 50.7% | 1690 | 82.2 |
| 2分 | 0 | 0 | 0 | 0 | - | - | - |

勝率は引き分けを除いた `勝 / (勝 + 負)`。

## 直近20局

| 日時 | 持ち時間 | 手番 | 相手 | 結果 | 手数 | 終局理由 | 自レート | 棋譜 | 悪手検出 |
|---|---|---|---|:-:|--:|---|--:|---|---|
| 2026-11-21 12:33 | 5分 | ☖後 | 相手(1854) | ● 負 | 119 | 時間切れ | 1690 | [CSA](data/csa/shogi5/y3654poqv5nz.csa) | - |
| 2026-11-21 09:16 | 5分 | ☗先 | 相手(1726) | ○ 勝 | 43 | 切断 | 1683 | [CSA](data/csa/shogi5/nioko8fzmolr.csa) | - |
| 2026-11-21 07:07 | 5分 | ☗先 | 相手(1721) | ● 負 | 74 | 詰み | 1688 | [CSA](data/csa/shogi5/9dhyq4lzhmx3.csa) | - |
| 2026-11-21 06:58 | 5分 | ☖後 | 相手(1353) | ○ 勝 | 80 | 詰み | 1687 | [CSA](data/csa/shogi5/1w1ltd7ai2eu.csa) | - |
| 2026-11-21 06:50 | 5分 | ☖後 | 相手(1341) | ○ 勝 | 118 | 詰み | 1687 | [CSA](data/csa/shogi5/g5kr3myb2xj6.csa) | - |
| 2026-11-21 02:21 | 5分 | ☗先 | 相手(1707) | ● 負 | 98 | 投了 | 1693 | [CSA](data/csa/shogi5/0yu3a38ozq1b.csa) | - |
| 2026-11-20 18:16 | 5分 | ☗先 | 相手(1691) | ● 負 | 76 | 投了 | 1699 | [CSA](data/csa/shogi5/asrk5esrf096.csa) | - |
| 2026-11-20 18:06 | 5分 | ☖後 | 相手(1217) | ● 負 | 127 | 時間切れ | 1703 | [CSA](data/csa/shogi5/byvz3kfm67xk.csa) | - |
| 2026-11-20 03:58 | 5分 | ☖後 | 相手(832) | ○ 勝 | 82 | 投了 | 1702 | [CSA](data/csa/shogi5/oqbytaftm4w5.csa) | - |
| 2026-11-20 03:07 | 5分 | ☗先 | 相手(1590) | ● 負 | 98 | 時間切れ | 1710 | [CSA](data/csa/shogi5/0x3vgvmqtip0.csa) | [水匠5](data/analysis/reports/0x3vgvmqtip0.md) 逃0 大3 悪3 疑3 |
| 2026-11-20 02:56 | 5分 | ☗先 | 相手(1725) | ● 負 | 88 | 詰み | 1711 | [CSA](data/csa/shogi5/v878s8ca6dcz.csa) | [水匠5](data/analysis/reports/v878s8ca6dcz.md) 逃0 大2 悪2 疑2 |
| 2026-11-20 01:30 | 5分 | ☖後 | 相手(1656) | ○ 勝 | 74 | 投了 | 1706 | [CSA](data/csa/shogi5/67kn1hr0u1qx.csa) | [水匠5](data/analysis/reports/67kn1hr0u1qx.md) 逃0 大3 悪2 疑3 |
| 2026-11-20 00:30 | 5分 | ☖後 | 相手(1652) | ● 負 | 141 | 時間切れ | 1713 | [CSA](data/csa/shogi5/i733sdd6lfai.csa) | [水匠5](data/analysis/reports/i733sdd6lfai.md) 逃3 大0 悪1 疑3 |
| 2026-11-19 19:03 | 5分 | ☗先 | 相手(1960) | ● 負 | 92 | 時間切れ | 1716 | [CSA](data/csa/shogi5/893h0bwg0r2q.csa) | [水匠5](data/analysis/reports/893h0bwg0r2q.md) 逃0 大4 悪7 疑1 |
| 2026-11-19 18:53 | 5分 | ☖後 | 相手(1733) | ○ 勝 | 84 | 投了 | 1714 | [CSA](data/csa/shogi5/yhyaazl9prhk.csa) | [水匠5](data/analysis/reports/yhyaazl9prhk.md) 逃0 大0 悪1 疑2 |
| 2026-11-19 12:54 | 5分 | ☗先 | 相手(1676) | ○ 勝 | 77 | 投了 | 1708 | [CSA](data/csa/shogi5/ghbg9r4zvprp.csa) | [水匠5](data/analysis/reports/ghbg9r4zvprp.md) 逃0 大0 悪2 疑1 |
| 2026-11-19 03:46 | 5分 | ☖後 | 相手(1533) | ○ 勝 | 120 | 詰み | 1705 | [CSA](data/csa/shogi5/0ior84hk0pnq.csa) | [水匠5](data/analysis/reports/0ior84hk0pnq.md) 逃1 大11 悪2 疑3 |
| 2026-11-19 03:31 | 5分 | ☗先 | 相手(1713) | ○ 勝 | 103 | 時間切れ | 1699 | [CSA](data/csa/shogi5/w047ckz5gtbl.csa) | - |
| 2026-11-19 03:21 | 5分 | ☖後 | 相手(1549) | ○ 勝 | 2 | 投了 | 1696 | [CSA](data/csa/shogi5/6gjexq7tsau1.csa) | [水匠5](data/analysis/reports/6gjexq7tsau1.md) 逃0 大0 悪0 疑0 |
| 2026-11-19 03:21 | 5分 | ☗先 | 相手(1552) | ○ 勝 | 3 | 投了 | 1693 | [CSA](data/csa/shogi5/9oua8ago60l1.csa) | [水匠5](data/analysis/reports/9oua8ago60l1.md) 逃0 大0 悪0 疑0 |

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
