# Caelavi — カエラヴィMOD

この公開更新は制作資料と入口の4ファイルのみです。基点の公開製品コードは `ff3bba9`、資料に記録したローカル監査対象は未コミット差分を持つ `7f2fba9` 系で、後続のコード・XML・画像はこの更新に含めません。新規読者は制作引継ぎ正本の確定仕様・最初のタスクから始め、編集前に公開コードの実在を確認してください。

RimWorld 1.6向けカエラヴィ種族MODの開発リポジトリです。種族仕様・装備品目表と後続の採用差分を、[開発ロードマップ](docs/development-roadmap.md)に実装順と確認条件を整理しています。完成像を現在の試作範囲に限定しません。

**主軸はカエラヴィとして暮らし、コロニーを育てることです。** 工業化・自動化は生活・生産・装備・防衛を育てる手段。独立系女性記者の個人シナリオは任意の寄り道で、Caelaviを主役MODに据えないプレイヤー向けの入口にもなります。彼女の加入・進行・帰国/残留を、通常研究や工業化の必須条件にしません。これは設計方針で、追加機能の実装完了を示すものではありません。

監査対象のローカル試作には独立種族、左右の翼と義翼、手動展翼、卵生、民主共和国、特派員の加入、開始シナリオ3種、民生・軍用武器、制服、作業・戦闘メカの試作Defを収録しています。**現在の外見と装備画像は新規の仮表示で、正式デザインではありません。** 機能によって実機確認の深さが異なります。[現行状態と検証対象](docs/development-roadmap.md#現行状態の正本2026-10-05文書整理)で採用・実装・確認を区別し、日付付き記録へ案内しています。旧試作のコード・DLL・素材は移入していません。

## 現在の試作を使う

RimWorld 1.6、Biotech、Harmony、Vanilla Expanded Frameworkを用意し、このリポジトリをゲームの `Mods` に配置して有効化します。開発者モードのPawn生成では `Caelavi (development)` を選べます。開始メニューにはカエラヴィ専用シナリオ3種が入り、民主共和国は世界生成用の勢力として登録されています。シナリオの開始操作と長期プレイは今後の実機確認対象です。

macOSのSteam標準配置なら、現行の開発フォルダ `Caelavi` を `~/Library/Application Support/Steam/steamapps/common/RimWorld/RimWorldMac.app/Mods/` に置きます。開発中は同名フォルダへのシンボリックリンクでも構いません。同じ `packageId` の旧開発用MODがある場合は、重複しないようゲームの `Mods` フォルダ外へ退避します。ゲームを再起動し、メニューの「Mods」でCaelaviとVanilla Expanded Frameworkを有効にして変更を適用します。

macOSでは、ゲーム本体と前提MODのインストール先を環境変数で変更できます。`.NET SDK 8` を用い、ゲームや前提MODのDLLはローカル環境から参照してビルドします。参照DLLをリポジトリに同梱しません。`dotnet` がPATHにない場合は `DOTNET_BIN=/path/to/dotnet sh tools/build.sh` と指定します。

```sh
sh tools/build.sh
python3 tools/validate.py --game-data '/path/to/RimWorldMac.app/Data'
python3 tools/package.py --game-data '/path/to/RimWorldMac.app/Data'
```

`dist/Caelavi.zip` は2026-09-24の過去の試作成果物です。現行DLL・武器XMLと一致せず、後続の追加武器Defも未収録のため、現行版として使用・配布しません。パッケージ化の前にDLLをビルドしてください。`tools/run_smoke.py` は独立した保存先でロードを確認し、[配布対象外のセルフテスト](tools/selftest/README.md)は新規マップで一部の動作と保存再読込を確認します。現行の確認範囲と残る仕事は[ロードマップ](docs/development-roadmap.md)を参照してください。過去の実施結果は[日付付き検証記録](docs/verification-2026-09-24.md)に残しています。

前提MODの公開Workshop情報とローカルのSteam記録は、読み取り専用の更新確認（`docs/steam-dependency-check.md`、ローカル補助資料/実装・本公開には未同梱）で照合できます。ゲーム本体の公開最新版を判定できない場合は `UNKNOWN` と表示します。

## 最初に読むもの

制作を引き継ぐ場合は[制作引継ぎ正本](docs/large-content-expansion-design-2026-10-05.md)から読みます。会話履歴なしで、確定/提案/保留、編集場所、ビルド、5品見本の最初のタスク、受入テストへ進めます。ロードマップは現行確認状態の索引です。

| 資料 | 内容 |
|---|---|
| [開発ロードマップ](docs/development-roadmap.md) | 現行状態の正本。基本仕様・後続採用差分・実装・未確認・次工程・検証日付への入口 |
| [制作引継ぎ正本・詳細設計](docs/large-content-expansion-design-2026-10-05.md) | 確定仕様/提案/保留、実装場所、制作台帳、データ/UI、着手タスク、受入テストと履歴 |
| [初期試作の開発ガイド](docs/alpha-development-guide.md) | 採用済み仕様、素材方針、初期実装の接続点と未定事項の扱い |
| [種族仕様](docs/species-life-appearance-apparel-draft-2026-09-18.md) | 出生・成長・全員共通の羽・飛行・翼の負傷・衣服 |
| [装備・メカ品目表](docs/equipment-catalog-draft-2026-09-15.md) | 武器世代、民生品、衣服・防具、APC・IFV・戦車、共和国・特派員・研究交易 |
| [バニラ受精卵の調査](docs/vanilla-fertilized-eggs-research-2026-09-19.md) | Core XMLとDLLから確認した産卵・孵化・親情報の仕組みと接続が必要な点 |
| [VEFの利用方針と調査](docs/vef-gravity-flight-options-2026-09-20.md) | 採用した飛行バフ3種、実装候補、追加候補、確認済み範囲 |
| [バニラ衣服の参考台帳](docs/vanilla-apparel-reference.md) | 衣服対応のためのテキスト資料 |
| [資料の来歴と参照先](docs/sources-and-status.md) | 参照時点、資料の位置づけ、旧試作との関係 |
| [アルファ仮素材](docs/placeholder-art.md) | 新規描画の用途、生成方法、正式デザインとの区別 |
| 画像生成アイコン実験（`art/experiments/imagegen-2026-09-24/README.md`、ローカル補助資料/実装・本公開には未同梱） | 卵と翼ガードの比較用候補。現行のゲーム画像には未接続 |
| 画像生成アイコン v02（`art/experiments/imagegen-2026-09-24-v02/README.md`、ローカル補助資料/実装・本公開には未同梱） | 卵と翼ガードを仮表示として接続。どちらもデザイン未選定 |
| 画像生成の四方向案（`art/experiments/pawn-turnaround-imagegen-2026-09-24-v01/README.md`、ローカル補助資料/実装・本公開には未同梱） | 提示画像を雰囲気として使った外見比較用。ゲーム表示には未接続 |
| Steam依存・ゲーム版の確認（`docs/steam-dependency-check.md`、ローカル補助資料/実装・本公開には未同梱） | Harmony・VEFの公開更新時刻とローカル記録、ゲーム本体の版を確認 |
| [飛行の仮値](docs/flight-provisional-values.md)・[卵生の実装](docs/egg-alpha-implementation.md) | 採用事項と調整用の数値、実機確認点 |
| [義翼](docs/prosthetic-wing-alpha.md)・[翼ガード](docs/wing-guard-alpha.md)・[共和国勢力](docs/faction-provisional-values.md) | アルファ品目と勢力生成の仮設定 |
| [特派員加入イベント](docs/correspondent-alpha.md) | 保存可能な加入申し出と未確認事項 |
| [検証記録](docs/verification-2026-09-24.md) | 2026-09-24までの履歴。現行ビルドへの保証ではない |

## 開発の前提

- 採用済み仕様を土台に製品全体へ進めます。現在のビルドは試作として扱い、未定の数値は理由付きの仮値で調整します。細部を全て決めることを着手条件にしません。
- バニラの機能を可能な限り利用し、Vanilla Expanded Frameworkを前提MODにする方針です。
- 「採用済み」「候補」「調整用仮値」「実装済み」「ゲーム内確認済み」を区別します。
- 既存素材のコピー・色替え・旧作の再採用を前提にしません。外部の参照モデルやMODの名称を挙げることは、画像・コードの転載を意味しません。
- 初期の勢力はカエラヴィ民主共和国。連邦共和国の実装は後の更新です。採用済みの装備・メカ構想を引き継ぎ、品目表の候補を一括採用扱いにはしません。

この資料のために隣接フォルダ、元のRIM作業環境、RIM-Knowledgeのローカルコピーを用意する必要はありません。実装・検証時には、利用するRimWorld本体・DLC・前提MODを別途用意します。

開発を引き継ぐ場合は [AGENTS.md](AGENTS.md) も参照してください。
