# IFGプロジェクト レポート v1.1

これは v1.0 に続く補遺であり、第4章と第5章のみを収録する。

<!-- TOC autoanchor=true levels=1-3 -->

## 目次
- [第4章 実装・ハードウェア構成](#第4章-実装-ハードウェア構成)
  - [4.1 μ-cavity最適化](#41-μ-cavity最適化)
  - [4.2 SQUIDカップリング](#42-squidカップリング)
- [第5章 制御・デコヒーレンス抑制](#第5章-制御デコヒーレンス抑制)
  - [5.1 フラックスポンプ最適化](#51-フラックスポンプ最適化)
  - [5.2 Dynamical Decouplingシーケンス](#52-dynamical-decouplingシーケンス)

### 第4章 実装・ハードウェア構成

#### 4.1 μ-cavity最適化

本節ではμ-cavityの品質係数 \(Q\) を最大化しつつモード体積 \(V_{\text{mode}}\) を最小化する最適化手法について記述する。最適化では以下の目的関数
$$
J = -\alpha \ln Q(R, L, t) + \beta V_{\text{mode}}(R, L)
$$
を用いる。ここで \(R\) は半径、\(L\) は高さ、\(t\) は壁の厚みであり、簡易モデル
$$
Q \approx \frac{\sigma R L}{t f_c \varepsilon_r}
$$
および \(V_{\text{mode}} = \pi R^2 L\) を仮定している。`tools/cavity_optimize.py` は L-BFGS-B 法により \(J\) を数値的に最小化する。実行例は以下の通り。

```bash
$ python tools/cavity_optimize.py
Optimal R (m): 0.0198
Optimal L (m): 0.0500
Optimal t (m): 0.0007
Minimum J: 2.31
```

シミュレーションから得られた \(J\) と半径の関係を以下に示す。本章の計算結果は `tools/` 以下のスクリプトによって自動生成されたものである。

**図 4.1**: \(J\) と \(R\) の関係  
<!-- TODO: この図は tools/cavity_optimize.py 実行後に生成・コミットしてください -->
![](../plot/cavity_J_vs_R.png)

#### 4.2 SQUIDカップリング

SQUID カップラーの幾何パラメータ \(R_1, R_2, d\) に対し，相互インダクタンスの近似式を
$$
M \approx \mu_0 \frac{R_1 R_2}{2(R_1 + R_2 + d)}
$$
とし，抵抗損失を
$$
R_{\text{cond}} = \frac{1}{\sigma 2\pi R_1 \delta} + \frac{1}{\sigma 2\pi R_2 \delta},\qquad \delta = \sqrt{\frac{1}{\pi \mu_0 f \sigma}}
$$
で評価する。目的関数は
$$
J = \bigl(g_{\text{target}} - k_{\text{couple}} M\bigr)^2 + \lambda R_{\text{cond}}
$$
である。`tools/squid_coupler.py` を実行すると以下のような出力が得られる。

```bash
$ python tools/squid_coupler.py
Optimal R1 (m): 0.0049
Optimal R2 (m): 0.0061
Optimal d (m): 0.0023
Minimum J: 4.8e-3
```

以上より，目標結合強度を満たすパラメータ組を決定できる。

**図 4.2**: \(J\) と d の関係  
<!-- TODO: この図は tools/squid_coupler.py 実行後に生成・コミットしてください -->
![](../plot/squid_J_vs_d.png)

### 第5章 制御・デコヒーレンス抑制

#### 5.1 フラックスポンプ最適化

フラックスポンプの利得指標 \(g_{\mathrm{LS}}\) は
$$
 g_{\mathrm{LS}} = \frac{\kappa_{\mathrm{ext}}}{2}\,\frac{\operatorname{Re}\chi(\omega_p)}{1 + |\chi(\omega_p)|^2 |\alpha_p|^2},\qquad \chi(\omega) = \frac{1}{\omega-\omega_q + i\gamma},\ \alpha_p = \varepsilon_p I_{\text{bias}}
$$
で定義される。`tools/fluxpump_optimize.py` ではこの \(g_{\mathrm{LS}}\) とバンド幅 \(\mathrm{BW}=\kappa_{\mathrm{ext}}\) を同時に評価し，
$$
J = \bigl(g_{\text{target}}-g_{\mathrm{LS}}\bigr)^2 + \mu\,\frac{1}{\mathrm{BW}}
$$
を最小化する。実行例を示す。

```bash
$ python tools/fluxpump_optimize.py
ω_p [GHz]: 7.468
ε_p: 0.12
I_bias: 0.95
g_LS: 0.171
Minimum J: 1.2e-4
```

得られた \(g_{\mathrm{LS}}\) とポンプ周波数の関係例を以下に示す。生成されたグラフは `docs/plot/fluxpump_g_vs_freq.png` に保存される。

**図 5.1**: \(g_{\mathrm{LS}}\) とポンプ周波数の関係  
<!-- TODO: この図は tools/fluxpump_optimize.py 実行後に生成・コミットしてください -->
![](../plot/fluxpump_g_vs_freq.png)

#### 5.2 Dynamical Decouplingシーケンス

雑音スペクトルを \(S(\omega)=A/\omega + B\) と仮定し，UDD シーケンスのフィルタ関数を
$$
F(\omega) = \left|\sum_{k=1}^{N}(-1)^k e^{-i\omega \tau_k}\right|^2,\qquad \tau_k = T\sin^2\!\left(\frac{\pi k}{2(N+1)}\right)
$$
と定める。デコヒーレンス率は
$$
\Gamma_{\text{dec}} = \int_{\omega_{\text{min}}}^{\omega_{\text{max}}}\! \frac{S(\omega) F(\omega)}{\omega^2}\, d\omega
$$
で評価され，\(T_2=1/\Gamma_{\text{dec}}\) が得られる。`tools/dd_simulation.py` の実行例を示す。

```bash
$ python tools/dd_simulation.py
Γ_dec: 3.4e-9
1/T2: 2.9e8
```

パルス数 \(N\) に対する \(T_2\) の傾向を以下に示す。本節の結果も `tools/` スクリプトにより計算されたものである。

**図 5.2**: \(T_2\) とパルス数の関係  
<!-- TODO: この図は tools/dd_simulation.py 実行後に生成・コミットしてください -->
![](../plot/dd_T2_vs_N.png)

### 第7章 理論と物理(実験)対応関係のまとめ

#### 7.1 パラメータ相互依存モデル

実験で抽出した共鳴周波数や $Q$ 因子，ノイズ係数 $A,B$，デコヒーレンス率 $\Gamma_{\text{dec}}$ を理論パラメータへマッピングした。表7.1 に主要パラメータの対応関係を示す。

| 理論パラメータ | 実験値由来 |
| --- | --- |
| $\omega_0$ (fc\_GHz) | metrics.json |
| $Q_{\text{loaded}}$ | metrics.json |
| $A,B$ | noise\_fit.json |
| $\Gamma_{\text{dec}}$ | t2.json |

温度ドリフトから求めた係数を $\alpha_{\mathrm{temp}}$ とおき，$\omega(t)=\omega_0(1-\alpha_{\mathrm{temp}} t)$ と補正する。熱負荷の総和も同時にパラメータ更新へ反映した。

#### 7.2 実験誤差要因とモデルギャップ

測定系雑音，温度安定性，パルス再現性など複数の要因が理論値と実測値の差分として現れる。図7.4 に示すフローは，これら誤差源を段階的に切り分けるための概念図である。

#### 7.3 実測 vs 理論比較図

以下に共鳴スペクトル・ノイズスペクトル・DD 減衰の比較結果を示す。

**図 7.1**: 共鳴スペクトル比較
![](../plot/fig7_1.png)

**図 7.2**: ノイズスペクトル比較
![](../plot/fig7_2.png)

**図 7.3**: DD 減衰比較
![](../plot/fig7_3.png)

#### 7.4 章末まとめと今後の展望

本章では理論パラメータと実験結果の対応付けを行い，残差誤差を評価した。今後は温度ドリフトを抑制する実装改善と，大規模系への展開を検討する予定である。最後に誤差要因の整理図を図7.4 に示す。

**図 7.4**: 誤差要因フローチャート
![](../plot/fig7_4.png)
