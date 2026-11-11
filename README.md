# 将棋クエスト対局記録 — qwalks

最終更新: 2026-11-11T20:39:18+09:00　/　総対局数: **79**　/　悪手検出済み: **79**

> 対局は GitHub Actions が毎日自動収集し、悪手検出（将棋AIによる解析）はローカルで手動実行しています。生データ: [`data/games_summary.csv`](data/games_summary.csv)　AI 相談用: [`AI_CONTEXT.md`](docs/ai/AI_CONTEXT.md)　悪手検出の説明: [`docs/mistake_analysis.md`](docs/mistake_analysis.md)

**[次の一手 問題集](https://from-mattaka.github.io/shogi_quest/quiz/)** — 悪手検出で見つかった局面をブラウザで解けます（GitHub Pages）

## 持ち時間別サマリー

| 持ち時間 | 対局数 | 勝 | 負 | 分 | 勝率 | 最新レート | 平均手数 |
|---|--:|--:|--:|--:|--:|--:|--:|
| 10分 | 2 | 2 | 0 | 0 | 100.0% | 1843 | 66.5 |
| 5分 | 77 | 34 | 43 | 0 | 44.2% | 1657 | 81.6 |
| 2分 | 0 | 0 | 0 | 0 | - | - | - |

勝率は引き分けを除いた `勝 / (勝 + 負)`。

## 直近20局

| 日時 | 持ち時間 | 手番 | 相手 | 結果 | 手数 | 終局理由 | 自レート | 棋譜 | 悪手検出 |
|---|---|---|---|:-:|--:|---|--:|---|---|
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
| 2026-11-08 03:50 | 5分 | ☗先 | 相手(1443) | ● 負 | 94 | 詰み | 1696 | [CSA](data/csa/shogi5/08hldm71rauz.csa) | [水匠5](data/analysis/reports/08hldm71rauz.md) 逃0 大4 悪3 疑2 |
| 2026-11-07 14:03 | 5分 | ☖後 | 相手(1704) | ● 負 | 45 | 詰み | 1702 | [CSA](data/csa/shogi5/63qkmna4g2ds.csa) | [水匠5](data/analysis/reports/63qkmna4g2ds.md) 逃0 大1 悪0 疑0 |
| 2026-11-07 13:04 | 5分 | ☗先 | 相手(1511) | ○ 勝 | 91 | 投了 | 1699 | [CSA](data/csa/shogi5/w23hhrkby71v.csa) | [水匠5](data/analysis/reports/w23hhrkby71v.md) 逃1 大6 悪1 疑1 |
| 2026-11-07 12:54 | 5分 | ☖後 | 相手(1627) | ● 負 | 39 | 投了 | 1706 | [CSA](data/csa/shogi5/ti2v7qds1qrm.csa) | [水匠5](data/analysis/reports/ti2v7qds1qrm.md) 逃0 大2 悪3 疑2 |
| 2026-11-07 12:50 | 5分 | ☗先 | 相手(1548) | ● 負 | 78 | 詰み | 1715 | [CSA](data/csa/shogi5/y78upltfolnn.csa) | [水匠5](data/analysis/reports/y78upltfolnn.md) 逃0 大2 悪2 疑1 |
| 2026-11-07 12:43 | 5分 | ☗先 | 相手(1717) | ● 負 | 74 | 時間切れ | 1721 | [CSA](data/csa/shogi5/cu1szf4scqyy.csa) | [水匠5](data/analysis/reports/cu1szf4scqyy.md) 逃0 大3 悪5 疑1 |
| 2026-11-07 12:35 | 5分 | ☖後 | 相手(1542) | ● 負 | 85 | 投了 | 1730 | [CSA](data/csa/shogi5/7yprli13t5sq.csa) | [水匠5](data/analysis/reports/7yprli13t5sq.md) 逃0 大3 悪4 疑1 |
| 2026-11-07 10:14 | 5分 | ☗先 | 相手(2029) | ● 負 | 96 | 時間切れ | 1731 | [CSA](data/csa/shogi5/2pyf9x9cyrto.csa) | [水匠5](data/analysis/reports/2pyf9x9cyrto.md) 逃0 大6 悪7 疑0 |
| 2026-11-07 10:03 | 5分 | ☖後 | 相手(1695) | ○ 勝 | 74 | 投了 | 1726 | [CSA](data/csa/shogi5/vjm0el7hg9sz.csa) | [水匠5](data/analysis/reports/vjm0el7hg9sz.md) 逃0 大2 悪5 疑1 |

悪手検出の列: 評価関数名（レポートへのリンク）と、逃=詰み逃し・大=大悪手・悪=悪手・疑=疑問手 の件数。

## 悪手検出サマリー（評価関数・持ち時間別）

| 評価関数 | 持ち時間 | 解析局数 | 自分の手数 | 詰み逃し | 大悪手 | 悪手 | 疑問手 | 悪手率 | 1局あたり悪手 |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 水匠5 (`suisho5`) | 10分 | 2 | 67 | 0 | 2 | 2 | 7 | 6.0% | 2.00 |
| 水匠5 (`suisho5`) | 5分 | 77 | 3140 | 26 | 172 | 195 | 159 | 11.7% | 4.77 |

悪手率 = (大悪手 + 悪手) / 自分の手数。一覧: [`data/analysis/mistakes.csv`](data/analysis/mistakes.csv)
