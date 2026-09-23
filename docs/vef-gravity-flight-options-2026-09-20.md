# VEFを用いる飛行・重力操作の採用方針と候補

2026-09-20。ユーザー指定により**Vanilla Expanded Framework（VEF）を前提MODにする予定**。初期の展翼バフとして、**移動速度向上・射撃回避向上・地形による減速軽減**の3効果を採用する。荷重軽減や能動技などは追加候補。採用は設計方針の決定であり、コード実装・実機検証はまだ。

### 独立リポジトリでの扱い（2026-09-23）

本書は独立した`Daffodil-lab/Caelavi`のアルファ版開発に使う設計・調査資料である。旧RIM内の試作コード・DLL・描画ノードは移入せず、**既知の素材（PNG・KRA・ORA・Blender等）も当面使用しない。** 採用済みの3効果と維持負担を新たに実装し、未決定の数値は仮値と確定設定を分けて検証する。全候補の仕様確定をアルファ版着手の条件にしない。詳細は[アルファ版開発ガイド](alpha-development-guide.md)を参照する。

## 確認範囲

- 公式リポジトリの`main`、コミット`38f381513e341b89f49325817afcc59f371f375b`（2026-09-13）を取得し、`Source/VEF`・`1.6/Defs`・公式Wikiを照合した。Steam配布版との同一性は確認していない。
- 前提MODのpackageIdは`OskarPotocki.VanillaFactionsExpanded.Core`。当時の調査ではAbout.xmlやゲームのMOD構成を変更していない。本リポジトリでの依存設定と能力の接続は、今後の実装対象である。
- VEFを前提にすることは、他のVEコンテンツMODをまとめて前提にする指定ではない。
- 既定方針：片翼でも飛行可能。展翼バフは両翼健在で完全・片翼で減少・両翼欠損でなし。両翼欠損時のデメリットは候補。翼保護装備の着用中は展翼バフなし。
- 2026-09-20採用：展翼／収納を手動で切り替え、時間制限で自動終了しない継続可能な方式とする。飛行を使い始める時期は人間換算で約13歳。
- 2026-09-21採用：飛行の維持負担として、空腹の進行と休息ゲージの消耗を増やす。倍率は未定。

## 1. 採用する初期の展翼バフ

**展翼中の移動速度向上・射撃回避向上・地形による減速軽減**を初期の3効果とする。**荷重軽減**は生活・遠征向けの追加候補として残す。展翼／収納は手動切替で、時間制限による終了を設けず継続できる。**飛行中は空腹の進行と休息ゲージの消耗が増える**ことを維持負担として採用する。効果の数値・片翼時の減少率・空腹と休息消耗の倍率は未定。

飛行の使用開始は**人間換算で約13歳**とする。孵化直後がRimWorldの人間の3歳相当であることとは分け、孵化時から飛行可能とはしない。約13歳を内部年齢や成長段階へどう対応させるかは実装時に確認し、飛行以外の重力能力の習得時期は未定とする。

| 効果 | 状態 | プレイ上の効果 | 確認した土台 | 追加対応・範囲 |
|---|---|---|---|---|
| 移動速度向上 | 初期効果として採用 | 展翼中の移動を速くする | バニラのMoveSpeed | 翼・装備・展翼状態を判定して補正する。数値・片翼時の減少率は未定 |
| 射撃回避向上 | 初期効果として採用 | 展翼中、飛んでくる射撃を回避しやすくする | `VEF_RangedDodgeChance` | Hediff等で補正する案。弾道そのものを曲げる表現や、全種類の攻撃に対する防御ではない |
| 地形による減速軽減 | 初期効果として採用 | 通行可能な悪路の減速を抑える | VEFのFloatingまたは地形タグ別移動倍率 | 効果を採用し、実装方式は比較して選ぶ。両方式の併用は前提にしない |
| 荷重軽減 | 追加候補・未採用 | 遠征でより多くの荷物を持てる | `VEF_MassCarryCapacity` | 主にキャラバンの重量容量。マップ内で一度に運ぶスタック量は別処理として確認する |

採用した3効果は、翼を展開して移動を助け、被弾を避ける設定に対応する。身体や荷物を重力操作で支える応用は追加候補として扱う。本人・全装備の質量を一律ゼロにする実装は今回の採用範囲に含めない。

出典：[能力値定義](https://github.com/Vanilla-Expanded/VanillaExpandedFramework/blob/38f381513e341b89f49325817afcc59f371f375b/1.6/Defs/StatDefs/Stats_Pawns.xml)、[射撃回避処理](https://github.com/Vanilla-Expanded/VanillaExpandedFramework/blob/38f381513e341b89f49325817afcc59f371f375b/Source/VEF/Pawns/Harmony/Projectile_ImpactSomething.cs)、[重量容量の処理](https://github.com/Vanilla-Expanded/VanillaExpandedFramework/blob/38f381513e341b89f49325817afcc59f371f375b/Source/VEF/Pawns/StatWorkers/StatWorker_MassCarryCapacity.cs)。

## 2. 地形・飛行・見た目をどう表すか

地形による減速軽減は採用済み。以下のFloatingと地形別移動倍率は、その実装方式の候補であり、どちらを使うかは未選択。アニメーションの方式と短距離飛行アクションも、この合意では採用を確定しない。

### 地形の減速を避ける：Floating

`VEF.AnimalBehaviours.HediffComp_Floating`を、展翼中に付けるHediffへ組み込む候補。HediffはPawnに付く状態効果であり、病気だけを意味しない。

標準の地形・障害物による追加移動コストを外す処理がある。ただし、**壁・通行不能水域を越える経路を作るものではなく、罠回避・飛行アニメーションも付かない。** 人型を除外する分岐は確認されなかったが、カエラヴィでの動作は未検証。

Floating自体は有効／無効の二値。片翼時に地形効果を一定割合へ弱めるフィールドはない。両翼と片翼の差は移動速度・回避等で表すか、次の地形別方式を選ぶ。複数の付与元による登録・解除が競合し得るため、浮遊状態の付与元は一つにまとめる案。

出典：[Floating公式説明](https://github.com/Vanilla-Expanded/VanillaExpandedFramework/wiki/Floating)、[HediffComp_Floating](https://github.com/Vanilla-Expanded/VanillaExpandedFramework/blob/38f381513e341b89f49325817afcc59f371f375b/Source/VEF/AnimalBehaviours/HediffComps/HediffComp_Floating.cs)、[移動コスト処理](https://github.com/Vanilla-Expanded/VanillaExpandedFramework/blob/38f381513e341b89f49325817afcc59f371f375b/Source/VEF/AnimalBehaviours/Harmony/Pawn_PathFollower_CostToMoveIntoCell_Patch.cs)。

### 地形別に強さを設定：移動倍率

`VEF.Hediffs.HediffComp_MoveSpeedFactorByTerrainTag`と`moveSpeedFactorByTerrainTag`により、指定地形タグでの移動倍率を設定できる。両翼用・片翼用の異なる設定へ切り替える候補。通行不能地形を解禁する処理ではなく、経路探索の評価への反映も別問題。

**Floatingとこの倍率は代替案として比較する。** Floatingが同じ移動コスト処理の結果を上書きするため、同時に付ければ期待どおり累積すると扱わない。Propertiesの`compClass`接続もXML等で明示・確認する。

出典：[地形別HediffComp](https://github.com/Vanilla-Expanded/VanillaExpandedFramework/blob/38f381513e341b89f49325817afcc59f371f375b/Source/VEF/Hediffs/Comps/HediffComp_MoveSpeedFactorByTerrainTag.cs)、[Properties](https://github.com/Vanilla-Expanded/VanillaExpandedFramework/blob/38f381513e341b89f49325817afcc59f371f375b/Source/VEF/Hediffs/Comps/Properties/HediffCompProperties_MoveSpeedFactorByTerrainTag.cs)。

### 翼を動かす表示

`VEF.AnimalBehaviours.HediffComp_Animation`は、状態効果の追加・除去に合わせてAnimationDefを設定・解除する。新規に実装する翼用の描画ノードに展翼・浮遊の見た目を付ける候補。旧試作のノードや翼素材を移入する指定ではない。AnimationDefと描画ノードの対応、欠損側の非表示、他のアニメーションとの競合は調整が必要。描画だけで移動・防御効果は生じない。

出典：[公式Hediff Animation](https://github.com/Vanilla-Expanded/VanillaExpandedFramework/wiki/Hediff-Animation)、[ソース](https://github.com/Vanilla-Expanded/VanillaExpandedFramework/blob/38f381513e341b89f49325817afcc59f371f375b/Source/VEF/AnimalBehaviours/HediffComps/HediffComp_Animation.cs)。

### 短距離の飛行移動

`VEF.Abilities.AbilityPawnFlyer`はPawnFlyerを利用する移動アクションの土台。指定地点へ飛ぶ技の候補になるが、対象指定・発動・着地点判定の接続コードが必要。常時飛行する歩行置換の完成機能ではない。壁・水域・屋根・罠の扱いは、基底PawnFlyerと起動側の判定を確認して決める。

出典：[AbilityPawnFlyer](https://github.com/Vanilla-Expanded/VanillaExpandedFramework/blob/38f381513e341b89f49325817afcc59f371f375b/Source/VEF/Abilities/Things/AbilityPawnFlyer.cs)。

## 3. 重力の能動技・装備へ広げる候補

以下は追加候補であり、初期の展翼バフ3効果への合意によって追加採用されたものではない。

| 案 | VEFの土台 | 実装上の範囲 |
|---|---|---|
| 重圧 | AbilityDefの範囲指定＋`AbilityExtension_Hediff` | 対象へ時限の移動速度低下を付ける案。敵味方の対象条件を設定・確認する。地面に残り続ける重力領域とは別 |
| 斥力打撃 | `DamageWorker_PushBackAttackMelee`＋`DamageExtension.pushBackDistance` | 攻撃を受けたPawnを攻撃者から離れたセルへ移す。近接攻撃・武器向けの応用。滑らかな吹き飛び・吸引・物品運搬は別途実装 |
| 重力偏向盾 | `Ability_Barrier`または`HediffComp_Shield` | 時限の個人シールド等へ流用する案。耐久容量・回復・防ぐ攻撃・射撃との併用を設計する |
| APC・IFVの防護圏 | `CompShieldField` | Pawnを中心とする範囲シールドの候補。展開したUGVやドローンを援護する役割へつなげる。召喚機能は別途必要 |
| 戦車型メカの個体盾 | `CompShieldBubble` | メカ自身の防護用。自身の射撃可否やEMP時の挙動を確認して設定する |

`Ability_Barrier`の基盤にサイフォーカス必須の処理は確認されず、VEFを使うためにカエラヴィの重力能力をサイキャストと設定する必要はない。VEFとVanilla Psycasts Expandedの固有機能は区別する。

盾の種類で挙動が異なる。`HediffComp_Shield`の初期設定では使用者の射撃を禁止するため、射撃と両立させる場合は設定が必要。`CompShieldBubble`にはEMPで破壊される処理がある。これらを調整せず「射撃できる無敵の盾」として採用しない。

生体の偏向盾と、既定の「翼保護装備中は展翼バフなし」との関係は別途設計する。盾を追加して既定の装甲方針を暗黙に変更しない。

出典：[AbilityDef](https://github.com/Vanilla-Expanded/VanillaExpandedFramework/blob/38f381513e341b89f49325817afcc59f371f375b/Source/VEF/Abilities/Defs/AbilityDef.cs)、[Hediff付与拡張](https://github.com/Vanilla-Expanded/VanillaExpandedFramework/blob/38f381513e341b89f49325817afcc59f371f375b/Source/VEF/Abilities/ModExtensions/AbilityExtension_Hediff.cs)、[斥力打撃の土台](https://github.com/Vanilla-Expanded/VanillaExpandedFramework/blob/38f381513e341b89f49325817afcc59f371f375b/Source/VEF/Weapons/DamageWorkers/DamageWorker_PushBackAttackMelee.cs)、[個人バリア](https://github.com/Vanilla-Expanded/VanillaExpandedFramework/blob/38f381513e341b89f49325817afcc59f371f375b/Source/VEF/Abilities/Abilities/Ability_Barrier.cs)、[Hediff盾](https://github.com/Vanilla-Expanded/VanillaExpandedFramework/blob/38f381513e341b89f49325817afcc59f371f375b/Source/VEF/Hediffs/Comps/HediffComp_Shield.cs)、[範囲盾](https://github.com/Vanilla-Expanded/VanillaExpandedFramework/blob/38f381513e341b89f49325817afcc59f371f375b/Source/VEF/Apparels/Comps/CompShieldField.cs)、[個体盾](https://github.com/Vanilla-Expanded/VanillaExpandedFramework/blob/38f381513e341b89f49325817afcc59f371f375b/Source/VEF/Apparels/Comps/CompShieldBubble.cs)。

## 4. 翼の状態とVEFをつなぐ設計案

採用した3効果を翼の状態に連動させるため、カエラヴィ側に左右翼の状態・展翼状態・翼保護装備・飛行を使用できる成長段階を確認する処理を置く。具体的な接続方式は実装時に確認する。

1. 両翼健在／片翼／両翼欠損を判定する。欠損に至らない負傷の細かな補正は未決定。
2. 人間換算で約13歳から使用する展翼／収納の手動切替を接続する。展翼中かつ翼保護装備なしなら、両翼健在で全量・片翼で減少・両翼欠損でなしの方針に従い、Hediffの段階・能力値を設定する。時間経過だけでは終了させない。翼保護装備中は展翼バフを付けない。片翼でも飛行できる方針を維持する。
3. VEFの地形処理・射撃回避と、バニラの移動速度へ効果を反映する。地形処理は第2節の代替案から選ぶ。Floatingを選ぶ場合の二値効果と片翼時の弱化の表し方は、方式選定時に整合させる。
4. 飛行中の維持負担として、空腹の進行と休息ゲージの消耗を増加させる。倍率と既存の空腹・休息処理への接続方式は未定。手動で継続できる方針を維持し、固定の制限時間は設けない。
5. 荷重軽減や能動技を将来採用する場合は、重量容量、VEF AbilityDefの`powerStatFactors`・`rangeStatFactors`・`durationTimeStatFactors`等へ共通の重力能力値を接続する案を検討する。これらは初期効果の実装範囲には含めず、どの値を翼に連動させるかも追加採用時に決める。

VEFには対象指定・持続時間・再使用時間・Hediff付与などの部品がある。一方、今回の翼の数に応じた変化や装備との排他制御は、VEFが自動的に理解する仕様ではない。展翼切替を含む専用の接続処理を用意する。

維持負担は空腹進行と休息ゲージ消耗の増加として採用済み。その倍率、睡眠や気絶などに伴う自動解除・再開の詳細、空腹・休息ゲージが低下した際の解除閾値、効果の数値・片翼時の減少率、両翼欠損時のデメリット、飛行以外の重力能力の習得時期は未決定。維持負担の採用だけで、これらの条件まで確定しない。

関連：[種族仕様](species-life-appearance-apparel-draft-2026-09-18.md)、[装備・メカ品目表](equipment-catalog-draft-2026-09-15.md)。
