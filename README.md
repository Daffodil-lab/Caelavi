# Caelavi — カエラヴィMODアルファ版

RimWorld 1.6向けカエラヴィ種族MODのアルファ版です。2026-09-23時点の決定事項を仕様・品目表・実装調査として収録しています。

`About/`、`1.6/`、`Languages/`、`Textures/`、`Source/` に独立種族のアルファ版を実装しています。左右の翼と義翼、手動展翼、卵生、民主共和国の最小勢力、特派員の加入イベント、翼保護装備を試作しました。**現在の外見は新規の仮表示で、正式デザインではありません。** 旧試作のコード・DLL・素材は移入していません。各機能の実機確認状況は[検証記録](docs/verification-2026-09-24.md)を参照してください。

## 現在の試作を使う

RimWorld 1.6、Biotech、Harmony、Vanilla Expanded Frameworkを用意し、このリポジトリをゲームの `Mods` に配置して有効化します。開発者モードのPawn生成では `Caelavi (development)` を選べます。民主共和国は世界生成用の試作勢力として登録しています。カエラヴィ専用の開始シナリオは未実装です。

macOSでは、ゲーム本体と前提MODのインストール先を環境変数で変更できます。`.NET SDK 8` を用い、ゲームや前提MODのDLLはローカル環境から参照してビルドします。参照DLLをリポジトリに同梱しません。

```sh
sh tools/build.sh
python3 tools/validate.py --game-data '/path/to/RimWorldMac.app/Data'
python3 tools/package.py --game-data '/path/to/RimWorldMac.app/Data'
```

生成物は `dist/Caelavi-alpha.zip` です。`tools/run_smoke.py` は独立した保存先でロードを確認します。実施範囲と残る確認は [検証記録](docs/verification-2026-09-24.md) に分けて記載しています。

## 最初に読むもの

| 資料 | 内容 |
|---|---|
| [アルファ版の開発ガイド](docs/alpha-development-guide.md) | 開発の進め方、素材方針、実装候補、動作確認、未定事項の扱い |
| [種族仕様](docs/species-life-appearance-apparel-draft-2026-09-18.md) | 出生・成長・全員共通の羽・飛行・翼の負傷・衣服 |
| [装備・メカ品目表](docs/equipment-catalog-draft-2026-09-15.md) | 武器世代、民生品、衣服・防具、APC・IFV・戦車、共和国・特派員・研究交易 |
| [バニラ受精卵の調査](docs/vanilla-fertilized-eggs-research-2026-09-19.md) | Core XMLとDLLから確認した産卵・孵化・親情報の仕組みと接続が必要な点 |
| [VEFの利用方針と調査](docs/vef-gravity-flight-options-2026-09-20.md) | 採用した飛行バフ3種、実装候補、追加候補、確認済み範囲 |
| [バニラ衣服の参考台帳](docs/vanilla-apparel-reference.md) | 衣服対応のためのテキスト資料 |
| [資料の来歴と参照先](docs/sources-and-status.md) | 参照時点、資料の位置づけ、旧試作との関係 |
| [アルファ仮素材](docs/placeholder-art.md) | 新規描画の用途、生成方法、正式デザインとの区別 |
| [飛行の仮値](docs/flight-provisional-values.md)・[卵生の実装](docs/egg-alpha-implementation.md) | 採用事項と調整用の数値、実機確認点 |
| [義翼](docs/prosthetic-wing-alpha.md)・[翼ガード](docs/wing-guard-alpha.md)・[共和国勢力](docs/faction-provisional-values.md) | アルファ品目と勢力生成の仮設定 |
| [特派員加入イベント](docs/correspondent-alpha.md) | 保存可能な加入申し出と未確認事項 |
| [検証記録](docs/verification-2026-09-24.md) | 静的検査、ゲームロード、ゲーム内動作、保存再読込の区別 |

## 開発の前提

- 対象はアルファ版。採用済み仕様を土台に試作し、未定の数値は仮値と明記して調整します。完成版の細部を全て決めることを着手条件にしません。
- バニラの機能を可能な限り利用し、Vanilla Expanded Frameworkを前提MODにする方針です。
- 「採用済み」「候補」「調整用仮値」「実装済み」「ゲーム内確認済み」を区別します。
- 既存素材のコピー・色替え・旧作の再採用を前提にしません。外部の参照モデルやMODの名称を挙げることは、画像・コードの転載を意味しません。
- 初期の勢力はカエラヴィ民主共和国。連邦共和国の実装は後の更新です。採用済みの装備・メカ構想を引き継ぎ、品目表の候補を一括採用扱いにはしません。

この資料のために隣接フォルダ、元のRIM作業環境、RIM-Knowledgeのローカルコピーを用意する必要はありません。実装・検証時には、利用するRimWorld本体・DLC・前提MODを別途用意します。

開発を引き継ぐ場合は [AGENTS.md](AGENTS.md) も参照してください。
