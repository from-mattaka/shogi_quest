# AI_CONTEXT — 将棋クエスト対局データ仕様書

このファイルは生成 AI に対局傾向の分析を相談する際のインプット用です。リポジトリ構造・データ定義・現在の統計・実データのサンプルをまとめています。

- 対象プレイヤー: `qwalks`
- データ更新日時: 2026-11-04T02:26:31+09:00
- 総対局数: 42（うち悪手検出済み 41）

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
│       └── reports/{game_id}.md # 対局別の解析レポート（盤面図・候補手つき）
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
| shogi5 | 40 | 19 | 21 | 0 | 47.5% | 77.6 | 1710〜1766 | 1724 | 2026-10-27 〜 2026-11-03 |

### ② time_mode × end_reason 別の勝敗件数

| time_mode | end_reason | 勝 | 負 | 分 | 計 |
|---|---|--:|--:|--:|--:|
| shogi10 | 投了 | 2 | 0 | 0 | 2 |
| shogi5 | 投了 | 12 | 11 | 0 | 23 |
| shogi5 | 詰み | 5 | 4 | 0 | 9 |
| shogi5 | 時間切れ | 2 | 6 | 0 | 8 |

### ③ ユニーク値一覧

- `handicap`: `平手` (42)
- `end_reason`: `投了` (25), `詰み` (9), `時間切れ` (8)

## 4. 最新3件のデータサンプル

### CSV

```csv
game_id,time_mode,played_at,handicap,sente_name,sente_rating,gote_name,gote_rating,my_turn,my_rating,opponent_name,opponent_rating,result,moves_count,end_reason,csa_rel_path,csa_hash,fetched_at
vlmg7sowkwdc,shogi5,2026-11-03 06:30:25,平手,qwalks,1724,相手,1663,SENTE,1724,相手,1663,WIN,61,投了,data/csa/shogi5/vlmg7sowkwdc.csa,733e8930a38f929e11d3d4b8a1e18eff31ec75c31b7a495bda9161c74deb704e,2026-11-04T02:26:31+09:00
63aputghegju,shogi5,2026-11-03 03:13:20,平手,qwalks,1717,相手,1763,SENTE,1717,相手,1763,WIN,91,時間切れ,data/csa/shogi5/63aputghegju.csa,2a2dd654186a5f5249ab84b42859d5b2c9a0fe1f44cf85f3e512e27e4e8800c9,2026-11-03T05:08:10+09:00
ph4tcdbgsa22,shogi5,2026-11-03 03:02:27,平手,qwalks,1714,相手,1580,SENTE,1714,相手,1580,WIN,3,投了,data/csa/shogi5/ph4tcdbgsa22.csa,9c1ed19b2425cdc50816dbea7efa0b652f203cd16f6504c095e0072bd63c19fb,2026-11-03T05:08:08+09:00
```

### 表

| game_id | time_mode | played_at | handicap | sente_name | sente_rating | gote_name | gote_rating | my_turn | my_rating | opponent_name | opponent_rating | result | moves_count | end_reason | csa_rel_path | csa_hash | fetched_at |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| vlmg7sowkwdc | shogi5 | 2026-11-03 06:30:25 | 平手 | qwalks | 1724 | 相手 | 1663 | SENTE | 1724 | 相手 | 1663 | WIN | 61 | 投了 | data/csa/shogi5/vlmg7sowkwdc.csa | 733e8930a38f929e11d3d4b8a1e18eff31ec75c31b7a495bda9161c74deb704e | 2026-11-04T02:26:31+09:00 |
| 63aputghegju | shogi5 | 2026-11-03 03:13:20 | 平手 | qwalks | 1717 | 相手 | 1763 | SENTE | 1717 | 相手 | 1763 | WIN | 91 | 時間切れ | data/csa/shogi5/63aputghegju.csa | 2a2dd654186a5f5249ab84b42859d5b2c9a0fe1f44cf85f3e512e27e4e8800c9 | 2026-11-03T05:08:10+09:00 |
| ph4tcdbgsa22 | shogi5 | 2026-11-03 03:02:27 | 平手 | qwalks | 1714 | 相手 | 1580 | SENTE | 1714 | 相手 | 1580 | WIN | 3 | 投了 | data/csa/shogi5/ph4tcdbgsa22.csa | 9c1ed19b2425cdc50816dbea7efa0b652f203cd16f6504c095e0072bd63c19fb | 2026-11-03T05:08:08+09:00 |

## 5. 最新 CSA 棋譜（1局分・全文）

`data/csa/shogi5/vlmg7sowkwdc.csa`（2026-11-03 06:30:25 / shogi5 / 自分=SENTE / WIN）

```csa
'Shogi Quest
N+qwalks(1724)
N-相手(1663)
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
-8384FU
+2726FU
-8485FU
+8877KA
-3334FU
+7968GI
-2277UM
+6877GI
-3142GI
+2625FU
-4233GI
+6978KI
-7162GI
+3948GI
-4132KI
+4746FU
-6364FU
+4847GI
-6263GI
+5968OU
-7374FU
+6766FU
-8173KE
+4756GI
-6152KI
+3736FU
-8281HI
+1716FU
-1314FU
+2937KE
-5162OU
+4948KI
-5354FU
+2829HI
-6272OU
+6858OU
-5262KI
+9796FU
-3344GI
+2524FU
-2324FU
+2924HI
-3435FU
+5647GI
-3536FU
+4736GI
-0025FU
+3745KE
-4445GI
+3645GI
-2133KE
+2434HI
-2526FU
+5868OU
-3242KI
+4554GI
-6354GI
+3454HI
-0027KA
+5424HI
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
| 水匠5 (`suisho5`) | shogi5 | 39 | 1520 | 16 | 85 | 93 | 84 | 11.7% | 18.3% | 4.56 | 7.13 |

悪手率 = (大悪手 + 悪手) / 自分の手数、疑問手以上率 = (詰み逃し + 大悪手 + 悪手 + 疑問手) / 自分の手数。

### ② 勝敗別の 1 局あたり件数

| 評価関数 | 結果 | 局数 | 1局あたり大悪手 | 1局あたり悪手 | 1局あたり疑問手 | 1局あたり詰み逃し |
|---|---|--:|--:|--:|--:|--:|
| 水匠5 (`suisho5`) | LOSS | 21 | 2.67 | 3.14 | 2.76 | 0.33 |
| 水匠5 (`suisho5`) | WIN | 20 | 1.55 | 1.45 | 1.65 | 0.45 |

### ③ 評価値が大きく動いた局面の傾向（手数帯 × カテゴリ）

| 手数帯 | 詰み逃し | 大悪手 | 悪手 | 疑問手 |
|---|--:|--:|--:|--:|
| 1〜30手 | 0 | 10 | 18 | 24 |
| 31〜60手 | 1 | 46 | 64 | 52 |
| 61〜90手 | 7 | 25 | 12 | 14 |
| 91〜120手 | 8 | 6 | 1 | 1 |
| 121手〜 | 0 | 0 | 0 | 0 |

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
63aputghegju,2026-11-03 03:13:20,shogi5,SENTE,85,詰み逃し,1.0000,0.0036,0.9964,#+17,-3372,7i8h,▲８八金(79),△６一銀(72) ▲７八金(88) △同桂成(66) ▲８二銀打 △８四玉(93) ▲８五金打,▲８二銀不成(71),7a8b,#+17,▲８二銀不成(71) △８四玉(93) ▲７八金(79) △９三桂(81) ▲同銀不成(82) △同玉(84),▲７八金(79),7i7h,#+19,▲７八金(79) △９五歩(94) ▲８二銀不成(71) △９四玉(93) ▲９五歩(96) △同玉(94),▲９二飛打,R*9b,-1456,▲９二飛打 △同香(91) ▲８二銀不成(71) △８四玉(93) ▲８五金打 △同馬(76),lnS+R4l/2s1g4/kppp2+P1p/p3p1p2/5n3/PP+bn4P/K1N1s1P1B/2s6/L1G2G2L b RG3P3p 85,suisho5,768068f0d534
6csegkafzmab,2026-10-31 01:07:21,shogi5,GOTE,82,詰み逃し,1.0000,0.0243,0.9757,#+17,-2216,S*6g,△６七銀打,▲８八玉(78) △３二歩打 ▲４二銀打 △８七飛成(81) ▲同玉(88) △７八角打,△６七角打,B*6g,#+17,△６七角打 ▲同金(58) △同歩成(66) ▲同玉(78) △６六歩打 ▲同玉(67),△８六桂打,N*8f,+833,△８六桂打 ▲同歩(87) △６七角打 ▲同金(58) △同歩成(66) ▲同玉(78),△３二歩打,P*3b,-46,△３二歩打 ▲８八玉(78) △４二角打 ▲３三桂不成(45) △同歩(32) ▲２五桂打,lr6l/3+P3k1/5pgp1/p3p3p/5N3/P1Pp1P1PP/1PN1P4/2K1G1+p2/L1R5L w G3SNP2bgsn2p 82,suisho5,768068f0d534
dsg657x1msx9,2026-10-31 09:51:35,shogi5,GOTE,100,大悪手,0.9993,0.0335,0.9658,+4336,-2017,S*4i,△４九銀打,▲同玉(38) △１二玉(13) ▲２二銀打 △２四歩(23) ▲３四銀(45) △６七角打,△４七銀打,S*4g,+4336,△４七銀打 ▲２八玉(38) △４八銀不成(47) ▲１四歩(15) △１二玉(13) ▲１一金(21),△４七歩打,P*4g,+4108,△４七歩打 ▲１四歩(15) △１二玉(13) ▲１一金(21) △同玉(12) ▲１三香打,△１二玉(13),1c1b,+2807,△１二玉(13) ▲１一金(21) △同玉(12) ▲２八玉(38) △４七銀打 ▲１三香打,l2g3Gl/3g5/1P1p3pk/p1+Rn1Sp1p/4pS2P/P1pl1+bN2/N5PP1/2r2PK2/6SNL w Pbgs4p 100,suisho5,768068f0d534
6k5xczmyfn8n,2026-10-27 21:11:18,shogi5,GOTE,62,大悪手,0.9565,0.0632,0.8933,+1854,-1618,4d5e,△５五角(44),▲６七金(58) △３一玉(22) ▲６六金(67) △１九角成(55) ▲６三歩打 △８二飛(62),△６八銀成(67),6g6h+,+1854,△６八銀成(67) ▲４四歩(45) △５八成銀(68) ▲同金(49) △２七歩成(26) ▲４七角打,△６八銀不成(67),6g6h,-912,△６八銀不成(67) ▲４四歩(45) △同歩(43) ▲４六桂打 △３一玉(22) ▲３四桂(46),△３一玉(22),2b3a,-1470,△３一玉(22) ▲４四歩(45) △６八銀成(67) ▲同角(77) △４二金(41) ▲４三歩成(44),ln1g1g2l/3r2sk1/2p1pp3/p4bpSp/1pP2P1P1/3p2PpP/PPBs5/3RG4/LN3GKNL w SN2p 62,suisho5,768068f0d534
```
