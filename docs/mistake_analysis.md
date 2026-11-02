# 悪手検出（`analyze_mistakes.py`）

将棋AI（やねうら王＋評価関数「水匠5」）で、収集した対局（`data/csa/`）を1局ずつ解析します。自分の指し手から **詰み逃し・大悪手・悪手・疑問手** を見つけ出し、盤面図と AI の候補手つきのレポートにまとめます。

- 対局の収集は GitHub Actions が毎日自動で行います（`collect.py`）
- 悪手検出は **ローカルのコンテナで、好きなときに手動で** 実行します（`analyze_mistakes.py`）。Actions ではエンジンを動かしません
- このドキュメントは「1局ごとに悪手を見つける」分析の説明です。蓄積したデータから「どんな局面でミスしやすいか」を探す傾向分析などは、今後別のスクリプト・ドキュメントとして追加する予定です。その際は、ここで出力する `data/analysis/mistakes.csv` や `moves/` が入力データになります

---

## 1. 何がわかるか

| 出力 | 場所 | 内容 |
|---|---|---|
| 対局別レポート | `data/analysis/reports/{game_id}.md` | 期待勝率の推移グラフ、1手ごとの評価値、課題局面ごとの盤面図・評価値・AI の候補手トップ3・相手の反撃手順 |
| 悪手・疑問手の一覧 | `data/analysis/mistakes.csv` | 全対局分の課題局面。1行 = 1手 |
| 1手ごとの推移 | `data/analysis/moves/{game_id}.csv` | 全手の評価値・期待勝率（グラフや傾向分析用） |
| 解析済みの台帳 | `data/analysis/analysis_index.csv` | 解析した対局ごとに、使ったエンジン・評価関数・設定・件数 |
| README | `README.md` | 直近の対局一覧の「悪手検出」列にレポートへのリンクと件数。評価関数・持ち時間別の悪手率 |
| AI 相談用 | `docs/ai/AI_CONTEXT.md` | 解析データのカラム定義、集計（持ち時間別・勝敗別・手数帯別）、低下幅が大きい手の上位 |

レポートは GitHub のブラウザ表示だけで振り返れるように作っています。盤面はテキストの盤面図（BOD 形式）、グラフは Mermaid で表示します。

### 判定カテゴリ

評価値そのものではなく、**期待勝率の低下幅**で判定します。

$$W(E) = \frac{1}{1 + \exp(-E/600)}$$

E は自分から見た評価値（cp）です。自分から詰みがあれば W = 100%、詰まされる局面なら W = 0% とします。

| カテゴリ | 条件 | README での略記 |
|---|---|---|
| 詰み逃し | 着手前は自分から詰みがあったのに、着手後は詰みが無くなった | 逃 |
| 大悪手 | 期待勝率が 20pt 以上下がった | 大 |
| 悪手 | 10pt 以上 20pt 未満 | 悪 |
| 疑問手 | 5pt 以上 10pt 未満 | 疑 |

勝率で判定するのは、次の2つを区別するためです。

- 勝勢の終盤で評価値が +3000 から +2000 に下がっても、勝率は 99.3% から 96.6% とほぼ変わらない → 悪手扱いしない
- 互角（評価値 0）の局面で -300 に下がると、勝率は 50% から 38% に落ちる → 悪手

実戦手が AI の最善手と同じ場合は、数値が多少下がっても対象外にします。

### 2段階探索

1. **第1パス（全手スキャン）**：開始局面から最終局面まで、全局面を短時間（0.15秒, MultiPV 1）で1回ずつ評価します。「k 手目を指した後の評価」をそのまま「k+1 手目を指す前の評価」として使い回すので、評価する局面は手数 + 1 個で済みます。
2. **第2パス（深掘り）**：自分の手のうち、次のどちらかに当てはまる局面だけを長め（2秒）に読み直します。
   - 実戦手が AI 最善手と異なり、勝率が 5pt 以上下がった
   - 詰みを逃した可能性がある

   読み直すのは、着手前の局面（MultiPV 3 で候補手トップ3を取る）と着手後の局面（相手の反撃手順を取る）の2つです。**カテゴリはこの第2パスの値で確定**します。第1パスで候補になっても、第2パスで基準を下回れば記録しません。

所要時間は1局あたり 30〜60 秒程度です（手数と候補の数によります）。

### レポートの読み方（課題局面の例）

```text
### 41手目 ▲２四歩(25) — 悪手
| | 着手前 | 着手後 | 差 |
| 期待勝率 | 58.3% | 44.1% | -14.2pt |
| 評価値 | +201 | -142 | |
（着手前の盤面図）
| 実戦  | ▲２四歩(25) | -142 | △同歩 ▲同飛 △８六歩 …   ← 実戦手の後に AI が読んだ相手の反撃手順
| AI 1位 | ▲４五桂(57) | +205 | ▲４五桂 △４四角 …      ← 候補手と、それを指した場合の評価値・読み筋
```

- 評価値はすべて**自分から見た値**です（プラスなら自分が有利）。
- 指し手は `▲７六歩(77)` の形で書きます。括弧内は移動元のマスです。
- 詰みは CSV では `#+5`（5手で詰ませる）または `#-3`（3手で詰まされる）、レポートでは「5手詰め」のように書きます。

### 生成AIに相談するとき

`docs/ai/AI_CONTEXT.md` を最初に渡すと、データ構造と集計値が伝わります。続けて `data/analysis/mistakes.csv` や、気になる対局のレポートを渡してください。例：

- 「悪手が序盤・中盤・終盤のどこに偏っているか、mistakes.csv から傾向を教えて」
- 「このレポートの 41 手目、AI 1位の手の狙いを解説して」

---

## 2. 初回セットアップ（1回だけ）

エンジンのビルドと評価関数のダウンロードは、**自分で次のコマンドを実行します**。devcontainer が自動で実行することはありません。

```bash
# (1) Python パッケージ（cshogi, py7zr）を .venv に入れる
#     devcontainer を作り直した場合は postCreateCommand で自動実行済み
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt -r requirements-analysis.txt

# (2) やねうら王をビルドし、水匠5 を取得する（数分。.engine/ 以下にだけ書き込む）
.venv/bin/python engine/setup_engine.py

# (3) 確認
.venv/bin/python analyze_mistakes.py --show-engine
```

`setup_engine.py` が行うのは次の処理だけです。sudo は使いません。

- `engine/engine.lock.json` に固定したタグとコミットのやねうら王を `git clone` し、`make` でビルドする。コミットが一致しなければ中止
- 水匠5 のアーカイブをダウンロードし、SHA-256 がロックファイルと一致することを確認してから `nn.bin` を取り出す
- 書き込み先は `.engine/`（Git 管理外）だけ。例外として、初回だけ `engine.lock.json` の `nn_bin_sha256` が空なら記入する（コミットしてください）

エンジンと評価関数は Git に入れません。`.engine/` はワークスペース内にあるので、コンテナを作り直しても残ります。

## 3. 普段の使い方

```bash
git pull                                   # Actions が取得した最新の対局を取り込む
.venv/bin/python analyze_mistakes.py                # 未解析の対局をすべて解析（新しい順）
git add data/analysis README.md docs/ai/AI_CONTEXT.md
git commit -m "analysis: ..." && git push
```

| コマンド | 用途 |
|---|---|
| `analyze_mistakes.py --dry-run` | 解析対象の一覧と所要時間の目安を表示（エンジンは起動しない） |
| `analyze_mistakes.py --limit 5` | 新しい順に5局だけ解析 |
| `analyze_mistakes.py --game ID` | 対局を指定（解析済みでも再解析） |
| `analyze_mistakes.py --since 2026-11-01 --mode shogi5` | 日付・持ち時間で絞り込み |
| `analyze_mistakes.py --force` | 解析済みも含めて全部再解析 |
| `analyze_mistakes.py --reanalyze-model-mismatch` | 評価関数を切り替えた後、古いモデルで解析した対局だけ再解析 |
| `analyze_mistakes.py --threads 4 --pass2-ms 3000` | 設定ファイルの値をその回だけ上書き |
| `analyze_mistakes.py --models` / `--show-engine` | 評価関数の確認（[engine_model.md](engine_model.md)） |
| `analyze_mistakes.py --regen-only` | README と AI_CONTEXT だけ作り直す（push で競合したときなど） |

- **途中で止めても大丈夫です。** Ctrl+C で中断しても、解析が終わった対局までは保存済みで、次回は続きから再開します。
- 次の対局は、フラグを付けなくても自動で再解析されます。
  - `games_summary.csv` 上で棋譜が変わった対局（`csa_hash` が変化）
  - `analysis_version` を上げた後の、古いバージョンで解析した対局
- 実行時に origin より遅れていれば警告が出ます（自動では pull しません）。

### push で README が競合したとき

README.md と AI_CONTEXT.md は Actions とローカルの両方が作り直します。ただし中身はデータ（`games_summary.csv` と `analysis_index.csv`）だけで決まります。競合したら、データ側を取り込んでから作り直せば解決します。

```bash
git checkout --theirs README.md docs/ai/AI_CONTEXT.md   # どちらでもよい
.venv/bin/python analyze_mistakes.py --regen-only
git add README.md docs/ai/AI_CONTEXT.md
```

翌日の Actions の実行でも同じ内容に作り直されます。

## 4. 設定（`config.json` の `analysis`）

| キー | 既定値 | 意味 |
|---|---|---|
| `analysis_version` | 1 | 判定ロジックや基準を変えたら上げる。上げると全局が再解析の対象になる |
| `threads` / `hash_mb` | 8 / 512 | エンジンのスレッド数と置換表 (MB)。環境変数 `ANALYSIS_THREADS` / `ANALYSIS_HASH_MB` でも上書きできる |
| `pass1.movetime_ms` / `pass1.nodes` | 150 / null | 第1パスの1局面あたりの思考時間。`nodes` を指定するとノード数で制限する（結果が CPU の速さに左右されない） |
| `pass2.movetime_ms` / `pass2.nodes` / `pass2.multipv` | 2000 / null / 3 | 第2パスの思考時間と候補手の数 |
| `winrate_scale` | 600 | 期待勝率の式の 600 |
| `thresholds` | dubious 0.05 / mistake 0.10 / blunder 0.20 | 疑問手 / 悪手 / 大悪手の境目（勝率の低下幅） |
| `pv_moves` | 6 | 読み筋を何手まで記録するか |
| `skip_opening_plies` | 0 | この手数までは判定しない（定跡部分を除きたいとき） |

評価関数の切り替えは `engine/engine.lock.json` で行います（[engine_model.md](engine_model.md)）。

## 5. 構成

```text
analyze_mistakes.py        # 悪手検出の入口（CLI）
analysis/
├── env.py                 # [共通] エンジン・評価関数の場所の解決と、ロックファイルとの照合
├── engine.py              # [共通] USI プロトコルでエンジンを動かすラッパー
├── kifu.py                # [共通] cshogi で CSA→USI・SFEN・盤面図・日本語表記に変換
├── schema.py              # [悪手検出] 出力ファイルのパス・カラム定義（標準ライブラリのみ。Actions 側の README 生成からも読む）
├── evaluator.py           # [悪手検出] 勝率変換と判定ロジック（純粋関数。tests/ でテスト）
├── runner.py              # [悪手検出] 1局分の2段階解析
└── report.py              # [悪手検出] CSV・Markdown の生成
engine/
├── engine.lock.json       # エンジンのタグ・コミット、評価関数の URL・SHA-256
└── setup_engine.py        # ビルドと評価関数の取得
.engine/                   # Git 管理外: ビルドしたバイナリと nn.bin
```

[共通] の3つはエンジンや棋譜を扱う部品で、今後追加する分析からも使い回せます。

`collect.py`（Actions）は `data/analysis/` を読むだけで書き込みません。`analyze_mistakes.py`（ローカル）は `data/csa/` と `games_summary.csv` を読むだけで書き込みません。両者が共通で作り直すのは README.md と AI_CONTEXT.md だけです。

テスト: `python3 -m unittest discover -s tests`
