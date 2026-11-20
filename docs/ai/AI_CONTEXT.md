# AI_CONTEXT — 将棋クエスト対局データ仕様書

このファイルは生成 AI に対局傾向の分析を相談する際のインプット用です。リポジトリ構造・データ定義・現在の統計・実データのサンプルをまとめています。

- 対象プレイヤー: `qwalks`
- データ更新日時: 2026-11-21T03:08:39+09:00
- 総対局数: 137（うち悪手検出済み 132）

## 1. ファイル配置

```text
.
├── data/
│   ├── games_summary.csv        # 全対局のマスター（UTF-8, ヘッダ行あり, LF, played_at 昇順）
│   ├── csa/
│   │   ├── shogi10/{game_id}.csa  # 10分切れ負けの棋譜
│   │   ├── shogi5/{game_id}.csa   # 5分切れ負けの棋譜
│   │   └── shogi2/{game_id}.csa   # 2分切れ負けの棋譜
│   └── analysis/                # 将棋AIによる悪手検出の結果（analyze_mistakes.py をローカルで手動実行して追加）
│       ├── analysis_index.csv   # 解析済み対局の台帳（使用エンジン・評価関数・件数）
│       ├── mistakes.csv         # 悪手・疑問手の一覧（全対局分）
│       ├── moves/{game_id}.csv  # 1手ごとの評価値・期待勝率の推移
│       ├── reports/{game_id}.md # 対局別の解析レポート（盤面図・候補手つき）
│       ├── reports/img/{game_id}_{ply}.svg # レポートの盤面画像（テキストの盤面図・SFEN はレポート本文にもある）
│       └── study/               # 序盤研究ドリル（analyze_opening_study.py の出力。盤面画像は study/img/）
├── docs/
│   ├── mistake_analysis.md      # 悪手検出（analyze_mistakes.py）の説明
│   ├── engine_model.md          # 評価関数の確認・切り替え手順
│   └── ai/AI_CONTEXT.md         # 本ファイル（自動生成）
└── README.md                    # 閲覧用ダッシュボード（自動生成）
```

- CSA ファイルは UTF-8・改行 LF。相手のユーザー名は `N+相手(レート)` のように伏せている。将棋クエストの CSA には終局行（`%TORYO` 等）が無いため、勝敗・終局理由は CSV 側を参照。
- `games_summary.csv` の 1 行 = 1 対局。`csa_rel_path` で棋譜と 1:1 対応。

## 2. games_summary.csv カラム定義

| # | カラム | 型 | 格納ルール |
|--:|---|---|---|
| 1 | `game_id` | str | 将棋クエストの対局 ID（英数字12桁程度）。主キー |
| 2 | `time_mode` | str | `shogi10` / `shogi5` / `shogi2`（10分 / 5分 / 2分切れ負け） |
| 3 | `played_at` | str (datetime) | 対局開始日時 `YYYY-MM-DD HH:MM:SS`（JST。API の UTC を変換） |
| 4 | `handicap` | str | 手合い `平手` / `香落ち` / `角落ち` / `飛車落ち` / `飛香落ち` / `二枚落ち` |
| 5 | `sente_name` | str | 先手の表示名（相手の場合は `相手` に置換） |
| 6 | `sente_rating` | int / 空 | 先手の対局時レート |
| 7 | `gote_name` | str | 後手の表示名（相手の場合は `相手` に置換） |
| 8 | `gote_rating` | int / 空 | 後手の対局時レート |
| 9 | `my_turn` | str | 自分の手番 `SENTE` / `GOTE` |
| 10 | `my_rating` | int / 空 | 自分の対局時レート |
| 11 | `opponent_name` | str | 常に `相手`（相手のユーザー名は公開しない方針で伏せている） |
| 12 | `opponent_rating` | int / 空 | 相手の対局時レート |
| 13 | `result` | str | 自分から見た結果 `WIN` / `LOSS` / `DRAW` |
| 14 | `moves_count` | int | CSA 内の実際の指し手数（投了・時間切れ等の終局アクションは含まない） |
| 15 | `end_reason` | str | 終局理由 `投了` / `時間切れ` / `詰み` / `トライ` / `切断` / `千日手` / `反則` / `連続王手千日手` |
| 16 | `csa_rel_path` | str | リポジトリルートからの CSA 相対パス `data/csa/{time_mode}/{game_id}.csa` |
| 17 | `csa_hash` | str | CSA ファイル（UTF-8, LF）の SHA-256 16進 |
| 18 | `fetched_at` | str (ISO8601) | 取得日時（JST, `+09:00` 付き） |

- 空値は空文字列（CSV 上は `,,`）。数値列も欠損時は空。
- `sente_*` / `gote_*` は盤上の手番基準、`my_*` / `opponent_*` は自分基準の重複表現。レートは対局開始時点の値。

## 3. 統計サマリー

### ① time_mode 別

| time_mode | 局数 | 勝 | 負 | 分 | 勝率 | 平均手数 | 自レート範囲 | 最新レート | 期間 |
|---|--:|--:|--:|--:|--:|--:|---|--:|---|
| shogi10 | 2 | 2 | 0 | 0 | 100.0% | 66.5 | 1836〜1843 | 1843 | 2026-09-12 〜 2026-09-12 |
| shogi5 | 135 | 68 | 67 | 0 | 50.4% | 82.0 | 1640〜1766 | 1693 | 2026-10-27 〜 2026-11-21 |

### ② time_mode × end_reason 別の勝敗件数

| time_mode | end_reason | 勝 | 負 | 分 | 計 |
|---|---|--:|--:|--:|--:|
| shogi10 | 投了 | 2 | 0 | 0 | 2 |
| shogi5 | 投了 | 36 | 24 | 0 | 60 |
| shogi5 | 時間切れ | 8 | 30 | 0 | 38 |
| shogi5 | 詰み | 23 | 12 | 0 | 35 |
| shogi5 | 切断 | 1 | 1 | 0 | 2 |

### ③ ユニーク値一覧

- `handicap`: `平手` (137)
- `end_reason`: `投了` (62), `時間切れ` (38), `詰み` (35), `切断` (2)

## 4. 最新3件のデータサンプル

### CSV

```csv
game_id,time_mode,played_at,handicap,sente_name,sente_rating,gote_name,gote_rating,my_turn,my_rating,opponent_name,opponent_rating,result,moves_count,end_reason,csa_rel_path,csa_hash,fetched_at
0yu3a38ozq1b,shogi5,2026-11-21 02:21:45,平手,qwalks,1693,相手,1707,SENTE,1693,相手,1707,LOSS,98,投了,data/csa/shogi5/0yu3a38ozq1b.csa,f99b7204c4cf1a46b2389c9d1cd917afe949bb25499a4813d8128034de9e3b91,2026-11-21T03:08:39+09:00
asrk5esrf096,shogi5,2026-11-20 18:16:41,平手,qwalks,1699,相手,1691,SENTE,1699,相手,1691,LOSS,76,投了,data/csa/shogi5/asrk5esrf096.csa,1bc3ba6998a482a78e354057edd5987723e4991a0226a73ef073f0f833b6cc42,2026-11-21T03:08:37+09:00
byvz3kfm67xk,shogi5,2026-11-20 18:06:20,平手,相手,1217,qwalks,1703,GOTE,1703,相手,1217,LOSS,127,時間切れ,data/csa/shogi5/byvz3kfm67xk.csa,340c886d9178086def5d8672463612a0a337c36ce959f576dd004208d6e8775a,2026-11-21T03:08:34+09:00
```

### 表

| game_id | time_mode | played_at | handicap | sente_name | sente_rating | gote_name | gote_rating | my_turn | my_rating | opponent_name | opponent_rating | result | moves_count | end_reason | csa_rel_path | csa_hash | fetched_at |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0yu3a38ozq1b | shogi5 | 2026-11-21 02:21:45 | 平手 | qwalks | 1693 | 相手 | 1707 | SENTE | 1693 | 相手 | 1707 | LOSS | 98 | 投了 | data/csa/shogi5/0yu3a38ozq1b.csa | f99b7204c4cf1a46b2389c9d1cd917afe949bb25499a4813d8128034de9e3b91 | 2026-11-21T03:08:39+09:00 |
| asrk5esrf096 | shogi5 | 2026-11-20 18:16:41 | 平手 | qwalks | 1699 | 相手 | 1691 | SENTE | 1699 | 相手 | 1691 | LOSS | 76 | 投了 | data/csa/shogi5/asrk5esrf096.csa | 1bc3ba6998a482a78e354057edd5987723e4991a0226a73ef073f0f833b6cc42 | 2026-11-21T03:08:37+09:00 |
| byvz3kfm67xk | shogi5 | 2026-11-20 18:06:20 | 平手 | 相手 | 1217 | qwalks | 1703 | GOTE | 1703 | 相手 | 1217 | LOSS | 127 | 時間切れ | data/csa/shogi5/byvz3kfm67xk.csa | 340c886d9178086def5d8672463612a0a337c36ce959f576dd004208d6e8775a | 2026-11-21T03:08:34+09:00 |

## 5. 最新 CSA 棋譜（1局分・全文）

`data/csa/shogi5/0yu3a38ozq1b.csa`（2026-11-21 02:21:45 / shogi5 / 自分=SENTE / LOSS）

```csa
'Shogi Quest
N+qwalks(1693)
N-相手(1707)
P1-KY-KE-GI-KI-OU-KI-GI-KE-KY
P2 * -HI *  *  *  *  * -KA * 
P3-FU-FU-FU-FU-FU-FU-FU-FU-FU
P4 *  *  *  *  *  *  *  *  * 
P5 *  *  *  *  *  *  *  *  * 
P6 *  *  *  *  *  *  *  *  * 
P7+FU+FU+FU+FU+FU+FU+FU+FU+FU
P8 * +KA *  *  *  *  * +HI * 
P9+KY+KE+GI+KI+OU+KI+GI+KE+KY
+
+7776FU
-3334FU
+2726FU
-8384FU
+2625FU
-2288UM
+7988GI
-3122GI
+8877GI
-2233GI
+3948GI
-4132KI
+6978KI
-8485FU
+4746FU
-5142OU
+4847GI
-7162GI
+4756GI
-1314FU
+1716FU
-7374FU
+5968OU
-6273GI
+6766FU
-6152KI
+3736FU
-7384GI
+2937KE
-7475FU
+5667GI
-7576FU
+6776GI
-4344FU
+4958KI
-3435FU
+0047KA
-0054KA
+2826HI
-3536FU
+4736KA
-5436KA
+2636HI
-0027KA
+3626HI
-2738UM
+3745KE
-4445FU
+0034FU
-3344GI
+2524FU
-2324FU
+2624HI
-0023FU
+2425HI
-0013KE
+2545HI
-4445GI
+4645FU
-6364FU
+4544FU
-0046FU
+0043GI
-5243KI
+4443TO
-3243KI
+0044FU
-4344KI
+0048FU
-0039HI
+0017KA
-3989RY
+1744KA
-0043GI
+0033KI
-4252OU
+3343KI
-5243OU
+4411UM
-0033FU
+0079KI
-8999RY
+7788GI
-9979RY
+7879KI
-0055KE
+3433TO
-2133KE
+0035HI
-0034KY
+3555HI
-0054KI
+5554HI
-5354FU
+0063KI
-4344OU
+1112UM
-8212HI
```

## 6. 悪手検出データ（analyze_mistakes.py: 将棋AIによる悪手・疑問手の抽出）

やねうら王＋評価関数（水匠など）で全手を評価し、自分の手のうち期待勝率を大きく下げた手を抽出したもの。解析方法の詳細は `docs/mistake_analysis.md`。

- 期待勝率 W(E) = 1 / (1 + exp(−E/600))（E は自分視点の評価値 cp。自分から詰みあり=1、詰まされ=0）
- 判定: `詰み逃し`（着手前に自分から詰みがあったのに逃した）/ `大悪手`（低下 ≥20pt）/ `悪手`（≥10pt）/ `疑問手`（≥5pt）。実戦手が AI 最善手と同じ場合は対象外
- 2段階探索: 第1パスで全局面を短時間評価 → 候補局面のみ第2パスで長時間・MultiPV 3 で再評価し判定を確定
- **評価関数が異なる解析結果は数値の基準が異なる**ため、集計は `model_id` ごとに分けて扱うこと

### ① 集計（評価関数 × time_mode 別）

| 評価関数 | time_mode | 解析局数 | 自分の手数 | 詰み逃し | 大悪手 | 悪手 | 疑問手 | 悪手率 | 疑問手以上率 | 1局あたり悪手 | 1局あたり疑問手以上 |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 水匠5 (`suisho5`) | shogi10 | 2 | 67 | 0 | 2 | 2 | 7 | 6.0% | 16.4% | 2.00 | 5.50 |
| 水匠5 (`suisho5`) | shogi5 | 130 | 5293 | 38 | 274 | 325 | 271 | 11.3% | 17.2% | 4.61 | 6.98 |

悪手率 = (大悪手 + 悪手) / 自分の手数、疑問手以上率 = (詰み逃し + 大悪手 + 悪手 + 疑問手) / 自分の手数。

### ② 勝敗別の 1 局あたり件数

| 評価関数 | 結果 | 局数 | 1局あたり大悪手 | 1局あたり悪手 | 1局あたり疑問手 | 1局あたり詰み逃し |
|---|---|--:|--:|--:|--:|--:|
| 水匠5 (`suisho5`) | LOSS | 64 | 2.55 | 3.14 | 2.39 | 0.20 |
| 水匠5 (`suisho5`) | WIN | 68 | 1.66 | 1.85 | 1.84 | 0.37 |

### ③ 評価値が大きく動いた局面の傾向（手数帯 × カテゴリ）

| 手数帯 | 詰み逃し | 大悪手 | 悪手 | 疑問手 |
|---|--:|--:|--:|--:|
| 1〜30手 | 0 | 21 | 69 | 88 |
| 31〜60手 | 1 | 138 | 195 | 143 |
| 61〜90手 | 16 | 97 | 52 | 44 |
| 91〜120手 | 17 | 20 | 11 | 3 |
| 121手〜 | 4 | 0 | 0 | 0 |

### ④ `data/analysis/analysis_index.csv` カラム定義（1 行 = 解析済み 1 対局）

| # | カラム | 型 | 内容 |
|--:|---|---|---|
| 1 | `game_id` | str | 対局 ID（games_summary.csv と同じ）。主キー |
| 2 | `csa_hash` | str | 解析時点の CSA の SHA-256。games_summary.csv と異なれば再解析対象 |
| 3 | `analysis_version` | int | 判定ロジックのバージョン（config.json の analysis.analysis_version） |
| 4 | `engine_name` | str | エンジンが USI で返した名前（`id name`） |
| 5 | `engine_tag` | str | やねうら王のビルド元タグとビルド種別（例: `V9.00/YANEURAOU_ENGINE_NNUE/AVX2`） |
| 6 | `model_id` | str | 評価関数の ID（engine/engine.lock.json の models のキー。例: `suisho5`） |
| 7 | `model_name` | str | 評価関数の表示名（例: `水匠5`） |
| 8 | `nn_bin_sha256` | str | 解析に実際に使った nn.bin の SHA-256（解析時に計算） |
| 9 | `pass1_limit` | str | 第1パスの探索制限（例: `movetime=150ms` / `nodes=300000`） |
| 10 | `pass2_limit` | str | 第2パスの探索制限 |
| 11 | `pass2_multipv` | int | 第2パスの候補手数 |
| 12 | `threads` | int | エンジンのスレッド数 |
| 13 | `hash_mb` | int | 置換表サイズ (MB) |
| 14 | `my_moves` | int | 自分の指し手数（判定対象の手数） |
| 15 | `n_candidates` | int | 第1パスで深掘り対象になった局面数 |
| 16 | `n_mate_miss` | int | 詰み逃しの数 |
| 17 | `n_blunder` | int | 大悪手の数 |
| 18 | `n_mistake` | int | 悪手の数 |
| 19 | `n_dubious` | int | 疑問手の数 |
| 20 | `elapsed_sec` | float | 1局の解析にかかった秒数 |
| 21 | `analyzed_at` | str (ISO8601) | 解析日時（JST） |

### ⑤ `data/analysis/mistakes.csv` カラム定義（1 行 = 抽出された 1 手）

| # | カラム | 型 | 内容 |
|--:|---|---|---|
| 1 | `game_id` | str | 対局 ID |
| 2 | `played_at` | str | 対局日時（JST） |
| 3 | `time_mode` | str | `shogi10` / `shogi5` / `shogi2` |
| 4 | `my_turn` | str | 自分の手番 `SENTE` / `GOTE` |
| 5 | `ply` | int | 手数（その手が何手目か） |
| 6 | `category` | str | `詰み逃し` / `大悪手` / `悪手` / `疑問手` |
| 7 | `winrate_before` | float | 着手前の期待勝率（自分視点, 0〜1） |
| 8 | `winrate_after` | float | 着手後の期待勝率（自分視点, 0〜1） |
| 9 | `winrate_drop` | float | 期待勝率の低下幅 = before − after |
| 10 | `eval_before` | str | 着手前の評価値（自分視点）。`+350` のような cp、詰みは `#+5`（5手で詰ませる）/`#-3`（3手で詰まされる） |
| 11 | `eval_after` | str | 着手後の評価値（自分視点, 同上） |
| 12 | `move_usi` | str | 実戦の指し手（USI 形式） |
| 13 | `move_ja` | str | 実戦の指し手（日本語。`▲７六歩(77)` 形式） |
| 14 | `reply_pv` | str | 実戦手の後の相手からの反撃手順（読み筋の先頭, 日本語, 空白区切り） |
| 15 | `cand1_move` | str | AI 推奨1位の指し手（日本語） |
| 16 | `cand1_usi` | str | AI 推奨1位の指し手（USI） |
| 17 | `cand1_eval` | str | AI 推奨1位を指した場合の評価値（自分視点） |
| 18 | `cand1_pv` | str | AI 推奨1位の読み筋（日本語, 空白区切り） |
| 19 | `cand2_move` | str | 2位（以下同様。候補が無い場合は空） |
| 20 | `cand2_usi` | str | 同上 |
| 21 | `cand2_eval` | str | 同上 |
| 22 | `cand2_pv` | str | 同上 |
| 23 | `cand3_move` | str | 3位 |
| 24 | `cand3_usi` | str | 同上 |
| 25 | `cand3_eval` | str | 同上 |
| 26 | `cand3_pv` | str | 同上 |
| 27 | `sfen_before` | str | 着手直前の局面（SFEN） |
| 28 | `model_id` | str | 解析に使った評価関数の ID |
| 29 | `nn_bin_sha12` | str | 解析に使った nn.bin の SHA-256 先頭12文字 |

### ⑥ `data/analysis/moves/{game_id}.csv` カラム定義（1 行 = 1 手）

| # | カラム | 型 | 内容 |
|--:|---|---|---|
| 1 | `ply` | int | 手数。0 は開始局面 |
| 2 | `mover` | str | その手を指した側 `SENTE` / `GOTE`（ply 0 は空） |
| 3 | `is_my_move` | int | 自分の手なら 1 |
| 4 | `move_usi` | str | 指し手（USI） |
| 5 | `move_ja` | str | 指し手（日本語） |
| 6 | `best_usi` | str | 着手前の局面での第1パス最善手（USI） |
| 7 | `best_ja` | str | 同（日本語） |
| 8 | `eval` | str | 着手後の評価値（自分視点。形式は mistakes.csv の eval_* と同じ） |
| 9 | `winrate` | float | 着手後の期待勝率（自分視点） |
| 10 | `winrate_drop` | float | 自分の手のみ: 着手前後の期待勝率の低下幅（第1パス値） |
| 11 | `category` | str | 第2パスで判定が確定した場合のカテゴリ |
| 12 | `model_id` | str | 評価関数の ID |

### ⑦ 低下幅が大きい手 上位5件（mistakes.csv の抜粋）

```csv
game_id,played_at,time_mode,my_turn,ply,category,winrate_before,winrate_after,winrate_drop,eval_before,eval_after,move_usi,move_ja,reply_pv,cand1_move,cand1_usi,cand1_eval,cand1_pv,cand2_move,cand2_usi,cand2_eval,cand2_pv,cand3_move,cand3_usi,cand3_eval,cand3_pv,sfen_before,model_id,nn_bin_sha12
5rtfbpyzr3ec,2026-10-29 18:53:36,shogi5,SENTE,103,大悪手,1.0000,0.0000,1.0000,+6398,#-3,6f6e,▲同玉(66),△６四金打 ▲６六玉(65) △５四桂打,▲５五玉(66),6f5e,+6398,▲５五玉(66) △７七馬(87) ▲６六桂打 △同銀(65) ▲４四玉(55) △３二桂打,▲同玉(66),6f6e,#-4,▲同玉(66) △６四金打 ▲６六玉(65) △５四桂打,▲７五玉(66),6f7e,#-2,▲７五玉(66) △７四金打,ln1S2+R1l/1ks+L3+P1/pppp4p/5ppN1/3s5/2PKP4/P+b1P4P/3gg4/8L b RBGSN4Pgnp 103,suisho5,768068f0d534
qxiged1ahfsn,2026-11-08 15:08:47,shogi5,GOTE,100,詰み逃し,1.0000,0.0000,1.0000,#+13,#-7,9i5i,△同龍(99),▲６七香打 △６六角打 ▲同龍(46) △５四玉(65) ▲６五龍(66) △４四玉(54),△３九金打,G*3i,#+13,△３九金打 ▲同玉(38) △５九龍(99) ▲４九金打 △１七角打 ▲同桂(29),△４九角打,B*4i,#+15,△４九角打 ▲同玉(38) △３九金打 ▲同玉(49) △５九龍(99) ▲４九金打,△２八金打,G*2h,#+15,△２八金打 ▲同玉(38) △３九角打 ▲同玉(28) △５九龍(99) ▲４九金打,l7l/5G3/4p1nS1/p1p4pp/3k5/5+R2P/PP3PPP1/6K2/+r3S2NL w L7P2b3g2s2n 100,suisho5,768068f0d534
bsxpb4pn004t,2026-11-11 07:55:59,shogi5,GOTE,86,大悪手,0.9998,0.0007,0.9992,+5270,-4380,R*5d,△５四飛打,▲５五桂打 △同飛(54) ▲同角(44) △７八龍(89) ▲６八桂打 △６九銀打,△２八飛打,R*2h,+5270,△２八飛打 ▲４八金打 △７八龍(89) ▲６八金打 △６七金打 ▲４九玉(58),△７八龍(89),8i7h,+2922,△７八龍(89) ▲６八銀打 △２八飛打 ▲４七玉(58) △５七金打 ▲３七玉(47),△５六飛打,R*5f,+2071,△５六飛打 ▲４七玉(58) △５七金打 ▲３七玉(47) △４四歩(43) ▲４一角打,l6nl/6gs1/3kpp1pp/2p2Bp2/p2N3P1/2P2PP1P/P8/4K4/L+r2P3L w B2G2S2Nrgs4p 86,suisho5,768068f0d534
63aputghegju,2026-11-03 03:13:20,shogi5,SENTE,85,詰み逃し,1.0000,0.0036,0.9964,#+17,-3372,7i8h,▲８八金(79),△６一銀(72) ▲７八金(88) △同桂成(66) ▲８二銀打 △８四玉(93) ▲８五金打,▲８二銀不成(71),7a8b,#+17,▲８二銀不成(71) △８四玉(93) ▲７八金(79) △９三桂(81) ▲同銀不成(82) △同玉(84),▲７八金(79),7i7h,#+19,▲７八金(79) △９五歩(94) ▲８二銀不成(71) △９四玉(93) ▲９五歩(96) △同玉(94),▲９二飛打,R*9b,-1456,▲９二飛打 △同香(91) ▲８二銀不成(71) △８四玉(93) ▲８五金打 △同馬(76),lnS+R4l/2s1g4/kppp2+P1p/p3p1p2/5n3/PP+bn4P/K1N1s1P1B/2s6/L1G2G2L b RG3P3p 85,suisho5,768068f0d534
ixmo9fev7z7u,2026-11-19 02:37:39,shogi5,SENTE,97,大悪手,1.0000,0.0102,0.9898,+35281,-2746,B*7g,▲７七角打,△５七玉(66) ▲２二角成(77) △４七玉(57) ▲３二馬(22) △５七金打 ▲６八銀打,▲６八金(79),7i6h,+35281,▲６八金(79) △７六玉(66) ▲７三馬(62) △８九飛成(39) ▲同玉(99) △７九金打,▲４八角打,B*4h,+5338,▲４八角打 △７九飛成(39) ▲同銀(88) △８六歩(85) ▲７三馬(62) △７六玉(66),▲５八銀(47),4g5h,+4611,▲５八銀(47) △６七金打 ▲７七角打 △７六玉(66) ▲６七銀(58) △同玉(76),lr5nl/3+BS1gs1/2n2p3/2p1p1p1p/pp1p1N3/2Pk1P2P/PP2PS1P1/LS5+p1/KNG3r1L b B2g2p 97,suisho5,768068f0d534
```
