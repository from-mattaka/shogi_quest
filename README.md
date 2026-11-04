# 将棋クエスト対局記録 — qwalks

最終更新: 2026-11-05T02:40:17+09:00　/　総対局数: **47**　/　悪手検出済み: **41**

> 対局は GitHub Actions が毎日自動収集し、悪手検出（将棋AIによる解析）はローカルで手動実行しています。生データ: [`data/games_summary.csv`](data/games_summary.csv)　AI 相談用: [`AI_CONTEXT.md`](docs/ai/AI_CONTEXT.md)　悪手検出の説明: [`docs/mistake_analysis.md`](docs/mistake_analysis.md)

**[次の一手 問題集](https://from-mattaka.github.io/shogi_quest/quiz/)** — 悪手検出で見つかった局面をブラウザで解けます（GitHub Pages）

## 持ち時間別サマリー

| 持ち時間 | 対局数 | 勝 | 負 | 分 | 勝率 | 最新レート | 平均手数 |
|---|--:|--:|--:|--:|--:|--:|--:|
| 10分 | 2 | 2 | 0 | 0 | 100.0% | 1843 | 66.5 |
| 5分 | 45 | 22 | 23 | 0 | 48.9% | 1733 | 79.4 |
| 2分 | 0 | 0 | 0 | 0 | - | - | - |

勝率は引き分けを除いた `勝 / (勝 + 負)`。

## 直近20局

| 日時 | 持ち時間 | 手番 | 相手 | 結果 | 手数 | 終局理由 | 自レート | 棋譜 | 悪手検出 |
|---|---|---|---|:-:|--:|---|--:|---|---|
| 2026-11-05 01:28 | 5分 | ☖後 | 相手(1608) | ● 負 | 115 | 時間切れ | 1733 | [CSA](data/csa/shogi5/vq6dz9aden01.csa) | - |
| 2026-11-05 00:57 | 5分 | ☖後 | 相手(1599) | ● 負 | 53 | 投了 | 1741 | [CSA](data/csa/shogi5/4vdv08093jtj.csa) | - |
| 2026-11-05 00:47 | 5分 | ☗先 | 相手(1846) | ○ 勝 | 119 | 投了 | 1734 | [CSA](data/csa/shogi5/dnk7otmi5vbw.csa) | - |
| 2026-11-05 00:22 | 5分 | ☖後 | 相手(1652) | ○ 勝 | 66 | 投了 | 1729 | [CSA](data/csa/shogi5/ibyp1c1n4fsv.csa) | - |
| 2026-11-04 23:19 | 5分 | ☗先 | 相手(1662) | ○ 勝 | 115 | 詰み | 1724 | [CSA](data/csa/shogi5/00hm06fbajl1.csa) | - |
| 2026-11-03 06:30 | 5分 | ☗先 | 相手(1663) | ○ 勝 | 61 | 投了 | 1724 | [CSA](data/csa/shogi5/vlmg7sowkwdc.csa) | - |
| 2026-11-03 03:13 | 5分 | ☗先 | 相手(1763) | ○ 勝 | 91 | 時間切れ | 1717 | [CSA](data/csa/shogi5/63aputghegju.csa) | [水匠5](data/analysis/reports/63aputghegju.md) 逃1 大5 悪2 疑1 |
| 2026-11-03 03:02 | 5分 | ☗先 | 相手(1580) | ○ 勝 | 3 | 投了 | 1714 | [CSA](data/csa/shogi5/ph4tcdbgsa22.csa) | [水匠5](data/analysis/reports/ph4tcdbgsa22.md) 逃0 大0 悪0 疑0 |
| 2026-11-02 18:02 | 5分 | ☖後 | 相手(1669) | ● 負 | 93 | 時間切れ | 1721 | [CSA](data/csa/shogi5/atd8b3u377ka.csa) | [水匠5](data/analysis/reports/atd8b3u377ka.md) 逃0 大6 悪6 疑5 |
| 2026-11-01 23:06 | 5分 | ☖後 | 相手(1640) | ○ 勝 | 26 | 投了 | 1716 | [CSA](data/csa/shogi5/hx9ye06ag4ck.csa) | [水匠5](data/analysis/reports/hx9ye06ag4ck.md) 逃0 大0 悪0 疑0 |
| 2026-11-01 19:44 | 5分 | ☗先 | 相手(1593) | ○ 勝 | 27 | 投了 | 1712 | [CSA](data/csa/shogi5/ozs25ba1ufp0.csa) | [水匠5](data/analysis/reports/ozs25ba1ufp0.md) 逃0 大0 悪0 疑0 |
| 2026-11-01 15:26 | 5分 | ☖後 | 相手(1699) | ● 負 | 81 | 投了 | 1719 | [CSA](data/csa/shogi5/g24bxc67f4bd.csa) | [水匠5](data/analysis/reports/g24bxc67f4bd.md) 逃0 大5 悪4 疑5 |
| 2026-11-01 07:50 | 5分 | ☗先 | 相手(1875) | ● 負 | 86 | 詰み | 1722 | [CSA](data/csa/shogi5/vzfpybyoukky.csa) | [水匠5](data/analysis/reports/vzfpybyoukky.md) 逃0 大1 悪5 疑1 |
| 2026-11-01 07:43 | 5分 | ☖後 | 相手(1775) | ● 負 | 95 | 投了 | 1727 | [CSA](data/csa/shogi5/vfwzjqhcsp8a.csa) | [水匠5](data/analysis/reports/vfwzjqhcsp8a.md) 逃0 大2 悪2 疑3 |
| 2026-11-01 02:19 | 5分 | ☗先 | 相手(1700) | ○ 勝 | 57 | 投了 | 1722 | [CSA](data/csa/shogi5/huc6okuziluw.csa) | [水匠5](data/analysis/reports/huc6okuziluw.md) 逃1 大3 悪2 疑0 |
| 2026-10-31 17:39 | 5分 | ☖後 | 相手(1507) | ○ 勝 | 78 | 時間切れ | 1719 | [CSA](data/csa/shogi5/lcfsldgp37mt.csa) | [水匠5](data/analysis/reports/lcfsldgp37mt.md) 逃0 大1 悪5 疑3 |
| 2026-10-31 17:30 | 5分 | ☗先 | 相手(1651) | ○ 勝 | 55 | 投了 | 1714 | [CSA](data/csa/shogi5/mdbd5x48ko53.csa) | [水匠5](data/analysis/reports/mdbd5x48ko53.md) 逃0 大1 悪1 疑2 |
| 2026-10-31 09:51 | 5分 | ☖後 | 相手(1655) | ● 負 | 111 | 時間切れ | 1721 | [CSA](data/csa/shogi5/dsg657x1msx9.csa) | [水匠5](data/analysis/reports/dsg657x1msx9.md) 逃1 大2 悪5 疑2 |
| 2026-10-31 09:41 | 5分 | ☗先 | 相手(1768) | ● 負 | 88 | 投了 | 1727 | [CSA](data/csa/shogi5/j28zuxvxl045.csa) | [水匠5](data/analysis/reports/j28zuxvxl045.md) 逃0 大3 悪2 疑1 |
| 2026-10-31 09:33 | 5分 | ☖後 | 相手(1907) | ○ 勝 | 64 | 投了 | 1718 | [CSA](data/csa/shogi5/6b1mcz1l326i.csa) | [水匠5](data/analysis/reports/6b1mcz1l326i.md) 逃0 大3 悪2 疑2 |

悪手検出の列: 評価関数名（レポートへのリンク）と、逃=詰み逃し・大=大悪手・悪=悪手・疑=疑問手 の件数。

## 悪手検出サマリー（評価関数・持ち時間別）

| 評価関数 | 持ち時間 | 解析局数 | 自分の手数 | 詰み逃し | 大悪手 | 悪手 | 疑問手 | 悪手率 | 1局あたり悪手 |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 水匠5 (`suisho5`) | 10分 | 2 | 67 | 0 | 2 | 2 | 7 | 6.0% | 2.00 |
| 水匠5 (`suisho5`) | 5分 | 39 | 1520 | 16 | 85 | 93 | 84 | 11.7% | 4.56 |

悪手率 = (大悪手 + 悪手) / 自分の手数。一覧: [`data/analysis/mistakes.csv`](data/analysis/mistakes.csv)
