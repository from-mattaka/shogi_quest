# 将棋クエスト対局記録 — qwalks

最終更新: 2026-11-15T01:15:49+09:00　/　総対局数: **99**　/　悪手検出済み: **89**

> 対局は GitHub Actions が毎日自動収集し、悪手検出（将棋AIによる解析）はローカルで手動実行しています。生データ: [`data/games_summary.csv`](data/games_summary.csv)　AI 相談用: [`AI_CONTEXT.md`](docs/ai/AI_CONTEXT.md)　悪手検出の説明: [`docs/mistake_analysis.md`](docs/mistake_analysis.md)

**[次の一手 問題集](https://from-mattaka.github.io/shogi_quest/quiz/)** — 悪手検出で見つかった局面をブラウザで解けます（GitHub Pages）

## 持ち時間別サマリー

| 持ち時間 | 対局数 | 勝 | 負 | 分 | 勝率 | 最新レート | 平均手数 |
|---|--:|--:|--:|--:|--:|--:|--:|
| 10分 | 2 | 2 | 0 | 0 | 100.0% | 1843 | 66.5 |
| 5分 | 97 | 43 | 54 | 0 | 44.3% | 1642 | 82.8 |
| 2分 | 0 | 0 | 0 | 0 | - | - | - |

勝率は引き分けを除いた `勝 / (勝 + 負)`。

## 直近20局

| 日時 | 持ち時間 | 手番 | 相手 | 結果 | 手数 | 終局理由 | 自レート | 棋譜 | 悪手検出 |
|---|---|---|---|:-:|--:|---|--:|---|---|
| 2026-11-15 00:42 | 5分 | ☗先 | 相手(1663) | ○ 勝 | 83 | 詰み | 1642 | [CSA](data/csa/shogi5/hm9k1flvfmqf.csa) | - |
| 2026-11-14 19:02 | 5分 | ☗先 | 相手(1593) | ● 負 | 94 | 詰み | 1649 | [CSA](data/csa/shogi5/dfl6vvybuzqw.csa) | - |
| 2026-11-14 18:50 | 5分 | ☖後 | 相手(1619) | ○ 勝 | 98 | 詰み | 1644 | [CSA](data/csa/shogi5/o402dz30yh03.csa) | - |
| 2026-11-14 18:42 | 5分 | ☖後 | 相手(1706) | ● 負 | 75 | 詰み | 1645 | [CSA](data/csa/shogi5/3ll02cic5ptm.csa) | - |
| 2026-11-14 18:39 | 5分 | ☗先 | 相手(1584) | ○ 勝 | 135 | 詰み | 1640 | [CSA](data/csa/shogi5/cuv3vgcaxi31.csa) | - |
| 2026-11-14 17:06 | 5分 | ☖後 | 相手(1721) | ● 負 | 85 | 時間切れ | 1645 | [CSA](data/csa/shogi5/emdmcoq2byj0.csa) | - |
| 2026-11-14 16:56 | 5分 | ☗先 | 相手(1661) | ● 負 | 50 | 投了 | 1651 | [CSA](data/csa/shogi5/0z1pz9l4tmt6.csa) | - |
| 2026-11-14 16:51 | 5分 | ☖後 | 相手(1569) | ○ 勝 | 74 | 時間切れ | 1646 | [CSA](data/csa/shogi5/1a8xq8ahv3rz.csa) | - |
| 2026-11-14 16:41 | 5分 | ☖後 | 相手(1953) | ● 負 | 71 | 切断 | 1648 | [CSA](data/csa/shogi5/mu18rwlbk7py.csa) | - |
| 2026-11-14 08:34 | 5分 | ☗先 | 相手(1676) | ● 負 | 116 | 時間切れ | 1654 | [CSA](data/csa/shogi5/aw3j1ufdtcjj.csa) | - |
| 2026-11-11 08:13 | 5分 | ☗先 | 相手(1656) | ● 負 | 96 | 投了 | 1657 | [CSA](data/csa/shogi5/hssbkifqjuc4.csa) | [水匠5](data/analysis/reports/hssbkifqjuc4.md) 逃0 大1 悪1 疑3 |
| 2026-11-11 07:55 | 5分 | ☖後 | 相手(1494) | ● 負 | 87 | 時間切れ | 1665 | [CSA](data/csa/shogi5/bsxpb4pn004t.csa) | [水匠5](data/analysis/reports/bsxpb4pn004t.md) 逃0 大3 悪4 疑6 |
| 2026-11-11 07:44 | 5分 | ☖後 | 相手(1590) | ○ 勝 | 62 | 投了 | 1661 | [CSA](data/csa/shogi5/nyrkl8frg18k.csa) | [水匠5](data/analysis/reports/nyrkl8frg18k.md) 逃0 大1 悪1 疑3 |
| 2026-11-11 07:41 | 5分 | ☗先 | 相手(1656) | ○ 勝 | 99 | 時間切れ | 1655 | [CSA](data/csa/shogi5/ts75kqlqwyjy.csa) | [水匠5](data/analysis/reports/ts75kqlqwyjy.md) 逃0 大1 悪3 疑4 |
| 2026-11-11 07:28 | 5分 | ☗先 | 相手(1487) | ○ 勝 | 111 | 詰み | 1651 | [CSA](data/csa/shogi5/gr88ed23d2qo.csa) | [水匠5](data/analysis/reports/gr88ed23d2qo.md) 逃0 大4 悪5 疑3 |
| 2026-11-11 04:39 | 5分 | ☗先 | 相手(1610) | ● 負 | 98 | 時間切れ | 1658 | [CSA](data/csa/shogi5/29w3l8boyi31.csa) | [水匠5](data/analysis/reports/29w3l8boyi31.md) 逃0 大2 悪4 疑4 |
| 2026-11-11 04:29 | 5分 | ☖後 | 相手(1690) | ● 負 | 81 | 詰み | 1664 | [CSA](data/csa/shogi5/eaao9ztqwfjx.csa) | [水匠5](data/analysis/reports/eaao9ztqwfjx.md) 逃0 大7 悪3 疑0 |
| 2026-11-11 04:19 | 5分 | ☖後 | 相手(1529) | ○ 勝 | 70 | 投了 | 1663 | [CSA](data/csa/shogi5/7dsyroqso91s.csa) | [水匠5](data/analysis/reports/7dsyroqso91s.md) 逃1 大0 悪5 疑2 |
| 2026-11-11 04:16 | 5分 | ☗先 | 相手(1589) | ○ 勝 | 91 | 詰み | 1658 | [CSA](data/csa/shogi5/krkqyboegd0p.csa) | [水匠5](data/analysis/reports/krkqyboegd0p.md) 逃1 大2 悪5 疑2 |
| 2026-11-11 04:06 | 5分 | ☖後 | 相手(1881) | ● 負 | 69 | 投了 | 1661 | [CSA](data/csa/shogi5/k39cdwfwahmq.csa) | [水匠5](data/analysis/reports/k39cdwfwahmq.md) 逃0 大2 悪3 疑3 |

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
