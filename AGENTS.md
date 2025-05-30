# AGENTS.md

IFGプロジェクトでは、以下のスクリプト群を互いに独立した「知能エージェント」とみなし、システム全体を構成するプロセスとして活用しています。本ドキュメントはそれらエージェントの役割を一覧化した内部向け資料です。

## simulate_muCavity.py

- **機能概要**：小型共振器(μキャビティ)の品質係数(Q)とモード体積を近似計算し、結果をJSONとPNGで保存するシンプルなシミュレータ。
- **入力ファイル/引数**：コマンドライン引数なし。スクリプト内で半径などのパラメータを定義。
- **出力ファイル**：`result/q_vs_r.json`、`docs/plot/mode_volume_vs_q.png`
- **エージェント的役割**：物理空間共鳴評価エージェント
- **依存ライブラリ**：`json`、`math`、`struct`、`zlib` (標準ライブラリ)

## simulate_fluxpump.py

- **機能概要**：フラックスポンプのパラメータ走査を行い、増幅ゲイン指標`g_LS`を計算。結果をJSONとヒートマップ画像に保存。
- **入力ファイル/引数**：コマンドライン引数なし。周波数やパワー範囲などを内部で設定。
- **出力ファイル**：`result/fluxpump_scan.json`、`docs/plot/fluxpump_gLS_heatmap.png`
- **エージェント的役割**：パラメトリック増幅解析エージェント
- **依存ライブラリ**：`numpy`、`matplotlib`、`json`

## layout_16Q_auto.py

- **機能概要**：16量子ビットの配置レイアウトを自動生成する。格子配置または六角配置を選択でき、ピッチをmm単位で指定可能。
- **入力ファイル/引数**：`--hex` (六角配置を使用)、`--pitch` (ピッチ指定)、`-o/--output` (出力先)
- **出力ファイル**：デフォルトは`result/qubit_layout_map.txt`
- **エージェント的役割**：配置設計エージェント
- **依存ライブラリ**：`argparse`、`math`

## map_state_to_layout.py

- **機能概要**：物理配置された量子ビットに論理状態ラベルを関連付け、結果をテキストに出力する。
- **入力ファイル/引数**：`--states` (ラベル一覧)、`-i/--input` (入力レイアウト)、`-o/--output` (出力先)
- **出力ファイル**：デフォルトは`result/qubit_state_map.txt`
- **エージェント的役割**：状態ラベルマッピングエージェント
- **依存ライブラリ**：`argparse`


## gen_logical_map.py

- **機能概要**：`qubit_state_map.txt` を解析し、論理状態から物理配置への対応表を JSON 形式で生成する。
- **入力ファイル/引数**：コマンドライン引数なし。`result/qubit_state_map.txt` を読み込む。
- **出力ファイル**：`result/logic_physical_map.json`
- **エージェント的役割**：論理状態–物理配置マッピングエージェント
- **依存ライブラリ**：`json`

## infer_coupling_candidates.py

- **機能概要**：論理状態の物理座標をもとに距離を計算し、近接ペアを"coupled"とした一覧JSONを生成する。
- **入力ファイル/引数**：コマンドライン引数なし。`result/logic_physical_map.json` を読み込む。
- **出力ファイル**：`result/coupling_candidates.json`
- **エージェント的役割**：結合候補推定エージェント
- **依存ライブラリ**：`json`、`math`、`os`

## gen_semantic_weights.py

- **機能概要**：物理距離に基づきカップリング候補へ指数減衰ウェイトを適用し、意味重み付きマップを生成する。
- **入力ファイル/引数**：`result/coupling_candidates.json`
- **出力ファイル**：`result/semantic_coupling_map.json`
- **エージェント的役割**：意味重み評価エージェント
- **依存ライブラリ**：`json`、`math`

## plot_semantic_coupling_graph.py

- **機能概要**：semantic_weight>0 のエッジのみを用いて論理グラフを描画する。
- **入力ファイル/引数**：`result/logic_physical_map.json`、`result/semantic_coupling_map.json`
- **出力ファイル**：`docs/plot/semantic_coupling_graph.png`
- **エージェント的役割**：意味構文グラフ可視化エージェント
- **依存ライブラリ**：`matplotlib`、`networkx`、`json`

## gen_semantic_tensor.py

- **機能概要**：semantic_weight 行列(16×16)を生成しCSVとJSONで保存する。
- **入力ファイル/引数**：`result/logic_physical_map.json`、`result/semantic_coupling_map.json`
- **出力ファイル**：`result/semantic_tensor.csv`、`result/semantic_tensor.json`
- **エージェント的役割**：意味テンソル生成エージェント
- **依存ライブラリ**：`csv`、`json`

## simulate_semantic_spread.py

- **機能概要**：semantic_tensor を用いて意味伝播を5ステップ分シミュレーションする。
- **入力ファイル/引数**：`result/logic_physical_map.json`、`result/semantic_tensor.json`
- **出力ファイル**：`result/semantic_spread_steps.json`、`docs/plot/semantic_spread_step5.png`
- **エージェント的役割**：意味伝播シミュレーションエージェント
- **依存ライブラリ**：`json`、`matplotlib`
