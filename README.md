# 将棋クエスト対局記録 — qwalks

最終更新: 2026-11-12T02:34:32+09:00　/　総対局数: **88**　/　悪手検出済み: **79**

> 対局は GitHub Actions が毎日自動収集し、悪手検出（将棋AIによる解析）はローカルで手動実行しています。生データ: [`data/games_summary.csv`](data/games_summary.csv)　AI 相談用: [`AI_CONTEXT.md`](docs/ai/AI_CONTEXT.md)　悪手検出の説明: [`docs/mistake_analysis.md`](docs/mistake_analysis.md)

**[次の一手 問題集](https://from-mattaka.github.io/shogi_quest/quiz/)** — 悪手検出で見つかった局面をブラウザで解けます（GitHub Pages）

## 持ち時間別サマリー

| 持ち時間 | 対局数 | 勝 | 負 | 分 | 勝率 | 最新レート | 平均手数 |
|---|--:|--:|--:|--:|--:|--:|--:|
| 10分 | 2 | 2 | 0 | 0 | 100.0% | 1843 | 66.5 |
| 5分 | 86 | 39 | 47 | 0 | 45.3% | 1657 | 82.3 |
| 2分 | 0 | 0 | 0 | 0 | - | - | - |

勝率は引き分けを除いた `勝 / (勝 + 負)`。

## 直近20局

| 日時 | 持ち時間 | 手番 | 相手 | 結果 | 手数 | 終局理由 | 自レート | 棋譜 | 悪手検出 |
|---|---|---|---|:-:|--:|---|--:|---|---|
| 2026-11-11 08:13 | 5分 | ☗先 | 相手(1656) | ● 負 | 96 | 投了 | 1657 | [CSA](data/csa/shogi5/hssbkifqjuc4.csa) | - |
| 2026-11-11 07:55 | 5分 | ☖後 | 相手(1494) | ● 負 | 87 | 時間切れ | 1665 | [CSA](data/csa/shogi5/bsxpb4pn004t.csa) | - |
| 2026-11-11 07:44 | 5分 | ☖後 | 相手(1590) | ○ 勝 | 62 | 投了 | 1661 | [CSA](data/csa/shogi5/nyrkl8frg18k.csa) | - |
| 2026-11-11 07:41 | 5分 | ☗先 | 相手(1656) | ○ 勝 | 99 | 時間切れ | 1655 | [CSA](data/csa/shogi5/ts75kqlqwyjy.csa) | - |
| 2026-11-11 07:28 | 5分 | ☗先 | 相手(1487) | ○ 勝 | 111 | 詰み | 1651 | [CSA](data/csa/shogi5/gr88ed23d2qo.csa) | - |
| 2026-11-11 04:39 | 5分 | ☗先 | 相手(1610) | ● 負 | 98 | 時間切れ | 1658 | [CSA](data/csa/shogi5/29w3l8boyi31.csa) | - |
| 2026-11-11 04:29 | 5分 | ☖後 | 相手(1690) | ● 負 | 81 | 詰み | 1664 | [CSA](data/csa/shogi5/eaao9ztqwfjx.csa) | - |
| 2026-11-11 04:19 | 5分 | ☖後 | 相手(1529) | ○ 勝 | 70 | 投了 | 1663 | [CSA](data/csa/shogi5/7dsyroqso91s.csa) | - |
| 2026-11-11 04:16 | 5分 | ☗先 | 相手(1589) | ○ 勝 | 91 | 詰み | 1658 | [CSA](data/csa/shogi5/krkqyboegd0p.csa) | - |
| 2026-11-10 12:20 | 5分 | ☗先 | 相手(1493) | ○ 勝 | 89 | 詰み | 1657 | [CSA](data/csa/shogi5/sawpejzfp7r1.csa) | [水匠5](data/analysis/reports/sawpejzfp7r1.md) 逃0 大0 悪3 疑1 |
| 2026-11-10 02:01 | 5分 | ☖後 | 相手(1949) | ● 負 | 101 | 時間切れ | 1659 | [CSA](data/csa/shogi5/sqjxvea27n7t.csa) | [水匠5](data/analysis/reports/sqjxvea27n7t.md) 逃1 大2 悪3 疑4 |
| 2026-11-10 00:07 | 5分 | ☖後 | 相手(1430) | ● 負 | 119 | 時間切れ | 1669 | [CSA](data/csa/shogi5/zmnamldfi3g8.csa) | [水匠5](data/analysis/reports/zmnamldfi3g8.md) 逃2 大0 悪4 疑4 |
| 2026-11-09 19:30 | 5分 | ☗先 | 相手(1669) | ● 負 | 98 | 時間切れ | 1675 | [CSA](data/csa/shogi5/0dqu4du7tlqd.csa) | [水匠5](data/analysis/reports/0dqu4du7tlqd.md) 逃0 大3 悪0 疑4 |
| 2026-11-09 18:21 | 5分 | ☖後 | 相手(1725) | ● 負 | 85 | 投了 | 1680 | [CSA](data/csa/shogi5/as3sxs4gkx2h.csa) | [水匠5](data/analysis/reports/as3sxs4gkx2h.md) 逃0 大3 悪2 疑0 |
| 2026-11-08 15:15 | 5分 | ☗先 | 相手(1824) | ○ 勝 | 3 | 切断 | 1673 | [CSA](data/csa/shogi5/nzorq52z66sq.csa) | [水匠5](data/analysis/reports/nzorq52z66sq.md) 逃0 大0 悪0 疑0 |
| 2026-11-08 15:08 | 5分 | ☖後 | 相手(1745) | ○ 勝 | 110 | 詰み | 1666 | [CSA](data/csa/shogi5/qxiged1ahfsn.csa) | [水匠5](data/analysis/reports/qxiged1ahfsn.md) 逃2 大0 悪3 疑2 |
| 2026-11-08 14:24 | 5分 | ☗先 | 相手(1436) | ○ 勝 | 103 | 詰み | 1663 | [CSA](data/csa/shogi5/494ierslpp4b.csa) | [水匠5](data/analysis/reports/494ierslpp4b.md) 逃0 大1 悪4 疑3 |
| 2026-11-08 14:13 | 5分 | ☖後 | 相手(1514) | ● 負 | 71 | 時間切れ | 1671 | [CSA](data/csa/shogi5/xmgjdpotb72n.csa) | [水匠5](data/analysis/reports/xmgjdpotb72n.md) 逃0 大3 悪4 疑2 |
| 2026-11-08 14:05 | 5分 | ☗先 | 相手(1529) | ● 負 | 96 | 時間切れ | 1680 | [CSA](data/csa/shogi5/3bbgkz3xe5hd.csa) | [水匠5](data/analysis/reports/3bbgkz3xe5hd.md) 逃0 大3 悪5 疑3 |
| 2026-11-08 13:54 | 5分 | ☖後 | 相手(1432) | ● 負 | 45 | 投了 | 1690 | [CSA](data/csa/shogi5/w1n83pk42w8n.csa) | [水匠5](data/analysis/reports/w1n83pk42w8n.md) 逃0 大1 悪3 疑0 |

悪手検出の列: 評価関数名（レポートへのリンク）と、逃=詰み逃し・大=大悪手・悪=悪手・疑=疑問手 の件数。

## 悪手検出サマリー（評価関数・持ち時間別）

| 評価関数 | 持ち時間 | 解析局数 | 自分の手数 | 詰み逃し | 大悪手 | 悪手 | 疑問手 | 悪手率 | 1局あたり悪手 |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 水匠5 (`suisho5`) | 10分 | 2 | 67 | 0 | 2 | 2 | 7 | 6.0% | 2.00 |
| 水匠5 (`suisho5`) | 5分 | 77 | 3140 | 26 | 172 | 195 | 159 | 11.7% | 4.77 |

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
