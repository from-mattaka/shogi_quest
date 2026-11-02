# 評価関数（モデル）の確認と切り替え

解析には「やねうら王（エンジン）＋評価関数（`nn.bin`）」を使います。現在の評価関数は **水匠5**（`suisho5`）です。

評価関数が違うと評価値の基準も変わるため、どの解析結果をどのモデルで出したかを必ず記録しています。

## 記録の仕組み

- 使えるモデルと取得元は `engine/engine.lock.json` に定義します。`active_model` が現在のモデルです。
- 解析の開始時に `nn.bin` の SHA-256 を計算し、ロックファイルの値と照合します。一致しなければ解析を中止します。
- 解析結果には、そのとき実際に使った `nn.bin` の SHA-256 を記録します。

| 記録先 | 記録内容 |
|---|---|
| `data/analysis/analysis_index.csv` | `engine_name`, `engine_tag`, `model_id`, `model_name`, `nn_bin_sha256`, 探索設定, `analyzed_at` |
| `data/analysis/mistakes.csv` | 各行に `model_id`, `nn_bin_sha12` |
| `data/analysis/moves/{game_id}.csv` | 各行に `model_id` |
| `data/analysis/reports/{game_id}.md` | 冒頭の「解析環境」表（エンジン、評価関数、SHA-256、設定、日時） |
| `README.md` | 「悪手検出」列のリンク文字（例: `水匠5`）と、評価関数別のサマリー |
| `docs/ai/AI_CONTEXT.md` | 評価関数別の集計（異なるモデルの数値は混ぜない） |

---

## 確認手順

### A. ある対局をどのモデルで解析したか

- **ブラウザで確認**：README の「悪手検出」列に評価関数名が出ています。リンク先レポートの「解析環境」表には SHA-256 まで載っています。
- **コマンドで確認**：

  ```bash
  grep '^<game_id>,' data/analysis/analysis_index.csv
  # 列: game_id,csa_hash,analysis_version,engine_name,engine_tag,model_id,model_name,nn_bin_sha256,...
  ```

### B. モデルごとの解析局数

```bash
.venv/bin/python analyze_mistakes.py --models
```

出力例：

```text
現在のモデル: 水匠5 [suisho5] nn.bin 1a2b3c4d5e6f
解析済み: 38 局
  水匠5 [suisho5] sha:1a2b3c4d5e6f  38 局  ← 現在
```

### C. 現在のモデルと実体のファイルが一致しているか

```bash
.venv/bin/python analyze_mistakes.py --show-engine      # エンジンを起動し、名前・モデル・SHA-256 を表示
.venv/bin/python engine/setup_engine.py --check  # 照合だけ行う（ダウンロードしない）
```

手動で照合する場合は、次の2つが同じ値になることを確かめます。

```bash
sha256sum .engine/eval/suisho5/nn.bin
grep nn_bin_sha256 engine/engine.lock.json
```

---

## モデルを切り替える手順

1. `engine/engine.lock.json` の `models` に新しいモデルを追加します。

   ```jsonc
   "suisho_new": {
     "display_name": "水匠○○",
     "edition": "YANEURAOU_ENGINE_NNUE",   // nn.bin の形式に合わせる（下の注意を参照）
     "source_page": "配布ページの URL",
     "url": "アーカイブの直接ダウンロード URL（.7z / .zip）",
     "archive_sha256": "sha256sum で計算した値",
     "nn_bin_sha256": ""                    // 空欄でよい（初回のセットアップで記入される）
   }
   ```

   `archive_sha256` は、配布元からダウンロードしたアーカイブで `sha256sum <ファイル>` を実行して求めます。

2. `"active_model"` を新しい ID に書き換えます。
3. `.venv/bin/python engine/setup_engine.py` を実行します。必要ならエンジンをビルドし直し、評価関数をダウンロードしてハッシュを照合します。
4. `.venv/bin/python analyze_mistakes.py --show-engine` で `OK` と表示されることを確認します。
5. 必要なら、古いモデルで解析した対局を解析し直します。

   ```bash
   .venv/bin/python analyze_mistakes.py --reanalyze-model-mismatch --dry-run   # 対象の確認
   .venv/bin/python analyze_mistakes.py --reanalyze-model-mismatch
   ```

   解析し直さなければ、古い結果は元のモデル名が付いたまま残ります。
6. `engine/engine.lock.json` と `data/analysis/` をコミットします。

**元のモデルに戻すとき**は、`active_model` を戻すだけです。`.engine/eval/<id>/` は消さずに残してあるので、ダウンロードし直す必要はありません。

### 注意: ビルド種別（`edition`）

NNUE の評価関数には形式（ネットワークの構造）がいくつかあり、形式ごとにやねうら王のビルドが異なります。

| edition | 対応する評価関数の例 |
|---|---|
| `YANEURAOU_ENGINE_NNUE` | halfKP 256x2-32-32（標準。水匠5 など） |
| `YANEURAOU_ENGINE_NNUE_HALFKP_1024X2_8_32` | halfKP 1024x2-8-32 |
| `YANEURAOU_ENGINE_NNUE_HALFKP_512X2_16_32` など | 配布元の説明に従う |

`edition` が違えば別のバイナリとして `.engine/bin/` に並べてビルドされます。形式が合わないと、`isready` の時点でエンジンが評価関数を読み込めずにエラーになります。

### エンジン本体を更新するとき

`engine.lock.json` の `engine.tag` と `engine.commit` を変えて `setup_engine.py` を実行します。commit は次のコマンドで確認できます。

```bash
git ls-remote https://github.com/yaneurao/YaneuraOu.git refs/tags/<tag>
```

エンジンを変えても評価値は変わり得ます。比較の一貫性を保ちたい場合は、`config.json` の `analysis.analysis_version` も上げてください。
