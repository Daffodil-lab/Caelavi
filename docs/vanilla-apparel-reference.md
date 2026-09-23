# バニラ衣服の参照台帳

移入日：2026-09-23。旧環境の`Apparel-Inventory.md`に保存されていた静的調査結果を、全行そのままテキストで収録した。元の抽出実行日はこの台帳では確認できない。画像・編集用ファイル・XML本体は含めない。

## 用途と採用状態

この台帳は、[装備品目案](equipment-catalog-draft-2026-09-15.md)および[出生・外見・衣服の検討稿](species-life-appearance-apparel-draft-2026-09-18.md)で衣服の着用レイヤーや被覆部位を検討するときの参照資料。掲載はカエラヴィ向け装備の採用・実装を意味しない。採用品・指定品・候補・補完の区別は装備品目案に従い、この台帳から採用状態を変更しない。

- 単純なXML親継承を解決した静的調査。MODパッチ・実行時処理は未適用。
- 元の調査はインストールされていた全DLCのファイルを対象にした。有効化状態、現在のゲーム版の全品目、カエラヴィMODが必要とするDLCの一覧とは別。
- `DLC`列の`Core`は本体。その他は当該DLCの定義に由来する。各DLCを前提にするか、条件付き対応にするかは実装時に決める。
- `Def`はゲーム内定義を照合するための識別子。`レイヤー`・`部位`は元の抽出値で、カエラヴィ側の追加身体部位に自動対応する保証はない。胴体防具の被覆だけで翼が保護されるとは扱わない。
- `着用パス`はゲームが画像参照に使うリソースキーを記録した文字列。ローカルファイルへのリンクでも、画像素材の同梱・採用・再利用許可でもない。
- `—`は元の抽出で着用パスの値を得ていない項目。その装備が表示されない、画像が存在しない、別の描画方式がない、とまでは断定しない。
- 表にはベルト類や使い切り装備も含む。衣服と同時に全品を装備できる意味ではなく、レイヤー競合・使用条件は実装時に確認する。
- 本移入ではXMLを再抽出していない。使用するRimWorld 1.6環境のXML・実行時パッチと照合し、着用・身体部位の被覆・保存／ロード後の表示をゲーム内で確認する必要がある。

## 静的台帳

|DLC|Def|レイヤー|部位|着用パス|
|---|---|---|---|---|
|Biotech|Apparel_KidRomper|OnSkin|Torso, Neck, Shoulders, Arms, Legs|Things/Pawn/Humanlike/Apparel/KidRomper/KidRomper|
|Biotech|Apparel_KidShirt|OnSkin|Torso, Shoulders|Things/Pawn/Humanlike/Apparel/KidShirt/KidShirt|
|Biotech|Apparel_KidPants|OnSkin|Legs|—|
|Biotech|Apparel_KidParka|Shell|Torso, Neck, Shoulders, Arms|Things/Pawn/Humanlike/Apparel/KidParka/KidParka|
|Biotech|Apparel_KidTribal|OnSkin|Torso, Legs|Things/Pawn/Humanlike/Apparel/KidTribal/KidTribalwear|
|Biotech|Apparel_KidHelmet|Overhead|UpperHead|Things/Pawn/Humanlike/Apparel/KidHelmet/KidHelmet|
|Biotech|Apparel_AirwireHeadset|Overhead|UpperHead|Things/Pawn/Humanlike/Apparel/AirwireHeadset/AirwireHeadset|
|Biotech|Apparel_ArrayHeadset|Overhead|UpperHead|Things/Pawn/Humanlike/Apparel/ArrayHeadset/ArrayHeadset|
|Biotech|Apparel_IntegratorHeadset|Overhead|UpperHead|Things/Pawn/Humanlike/Apparel/IntegratorHeadset/IntegratorHeadset|
|Biotech|Apparel_ArmorHelmetMechCommander|Overhead|FullHead|Things/Pawn/Humanlike/Apparel/MechcommanderHelmet/MechcommanderHelmet|
|Biotech|Apparel_ArmorHelmetMechlordHelmet|Overhead|FullHead|Things/Pawn/Humanlike/Apparel/MechlordHelmet/MechlordHelmet|
|Biotech|Apparel_GasMask|Overhead|FullHead|Things/Pawn/Humanlike/Apparel/GasMask/GasMask|
|Biotech|Apparel_MechlordSuit|Middle, Shell|Torso, Neck, Shoulders, Arms, Legs|Things/Pawn/Humanlike/Apparel/MechlordSuit/MechlordSuit|
|Biotech|Apparel_Bandolier|Shell|Torso|Things/Pawn/Humanlike/Apparel/HeavyBandolier/HeavyBandolier|
|Biotech|Apparel_Sash|Middle|Torso|Things/Pawn/Humanlike/Apparel/Sash/Sash|
|Biotech|Apparel_HeavyShield|Middle|Torso|—|
|Biotech|Apparel_PackControl|Belt|Waist|Things/Pawn/Humanlike/Apparel/ControlPack/ControlPack|
|Biotech|Apparel_PackBandwidth|Belt|Waist|Things/Pawn/Humanlike/Apparel/BandwidthPack/BandwidthPack|
|Biotech|Apparel_PackTox|Belt|Waist|Things/Pawn/Humanlike/Apparel/ToxPack/ToxPack|
|Anomaly|Apparel_CultistMask|Overhead|FullHead|Things/Pawn/Humanlike/Apparel/TwistedMask/TwistedMask|
|Anomaly|Apparel_CeremonialCultistMask|Overhead|FullHead|Things/Pawn/Humanlike/Apparel/WhispererMask/WhispererMask|
|Anomaly|Apparel_ShardPsychicShockLance|Belt|Waist|Things/Item/Artifact/ShardPsychicShockLance/ShardPsychicShockLance|
|Anomaly|Apparel_ShardPsychicInsanityLance|Belt|Waist|Things/Item/Artifact/ShardPsychicInsanityLance/ShardPsychicInsanityLance|
|Anomaly|Apparel_BiomutationLance|Belt|Waist|Things/Item/Artifact/BiomutationLance/BiomutationLance|
|Anomaly|Apparel_LabCoat|Shell|Torso, Neck, Shoulders, Arms|Things/Pawn/Humanlike/Apparel/LabCoat/LabCoat|
|Anomaly|Apparel_DisruptorFlarePack|Belt|Waist|Things/Pawn/Humanlike/Apparel/DisruptorFlarePack/DisruptorFlarePack|
|Anomaly|Apparel_PackTurret|Belt|Waist|Things/Pawn/Humanlike/Apparel/TurretPack/TurretPack|
|Anomaly|Apparel_DeadlifePack|Belt|Waist|Things/Pawn/Humanlike/Apparel/DeadlifePack/DeadlifePack|
|Royalty|Apparel_ShirtRuffle|OnSkin|Torso, Shoulders, Arms, Neck|Things/Pawn/Humanlike/Apparel/ShirtRuffle/ShirtRuffle|
|Royalty|Apparel_Corset|Middle|Torso|Things/Pawn/Humanlike/Apparel/CorsetRoyal/CorsetRoyal|
|Royalty|Apparel_VestRoyal|Middle|Torso|Things/Pawn/Humanlike/Apparel/VestRoyal/VestRoyal|
|Royalty|Apparel_RobeRoyal|Shell|Torso, Neck, Shoulders, Arms, Legs|Things/Pawn/Humanlike/Apparel/RoyalRobe/RoyalRobe|
|Royalty|Apparel_HatLadies|Overhead|UpperHead|Things/Pawn/Humanlike/Apparel/LadiesHat/LadiesHat|
|Royalty|Apparel_HatTop|Overhead|UpperHead|Things/Pawn/Humanlike/Apparel/TopHat/TopHat|
|Royalty|Apparel_Coronet|Overhead|UpperHead|Things/Pawn/Humanlike/Apparel/Coronet/Coronet|
|Royalty|Apparel_Crown|Overhead|UpperHead|Things/Pawn/Humanlike/Apparel/Crown/Crown|
|Royalty|Apparel_CrownStellic|Overhead|UpperHead|Things/Pawn/Humanlike/Apparel/CrownStellic/CrownStellic|
|Royalty|Apparel_Beret|Overhead|UpperHead|Things/Pawn/Humanlike/Apparel/Beret/Beret|
|Royalty|Apparel_PsyfocusHelmet|Overhead|UpperHead|Things/Pawn/Humanlike/Apparel/EltexHelmet/EltexHelmet|
|Royalty|Apparel_EltexSkullcap|Overhead|UpperHead|Things/Pawn/Humanlike/Apparel/EltexSkullcap/EltexSkullcap|
|Royalty|Apparel_PsyfocusShirt|OnSkin|Torso, Shoulders|Things/Pawn/Humanlike/Apparel/EltexShirt/EltexShirt|
|Royalty|Apparel_PsyfocusVest|Middle|Torso, Neck, Shoulders|Things/Pawn/Humanlike/Apparel/EltexVest/EltexVest|
|Royalty|Apparel_PsyfocusRobe|Shell|Torso, Neck, Shoulders, Arms, Legs|Things/Pawn/Humanlike/Apparel/EltexRobe/EltexRobe|
|Royalty|Apparel_ArmorReconPrestige|Middle, Shell|Torso, Neck, Shoulders, Arms, Legs|Things/Pawn/Humanlike/Apparel/PrestigeReconArmor/PrestigeReconArmor|
|Royalty|Apparel_ArmorHelmetReconPrestige|Overhead|FullHead|Things/Pawn/Humanlike/Apparel/PrestigeReconHelmet/PrestigeReconHelmet|
|Royalty|Apparel_ArmorMarinePrestige|Middle, Shell|Torso, Neck, Shoulders, Arms, Legs|Things/Pawn/Humanlike/Apparel/PrestigeMarineArmor/PrestigeMarineArmor|
|Royalty|Apparel_ArmorMarineHelmetPrestige|Overhead|FullHead|Things/Pawn/Humanlike/Apparel/PrestigeMarineHelmet/PrestigeMarineHelmet|
|Royalty|Apparel_ArmorCataphract|Middle, Shell|Torso, Neck, Shoulders, Arms, Legs|Things/Pawn/Humanlike/Apparel/CataphractArmor/CataphractArmor|
|Royalty|Apparel_ArmorHelmetCataphract|Overhead|FullHead|Things/Pawn/Humanlike/Apparel/CataphractArmorHelmet/CataphractHelmet|
|Royalty|Apparel_ArmorCataphractPrestige|Middle, Shell|Torso, Neck, Shoulders, Arms, Legs|Things/Pawn/Humanlike/Apparel/PrestigeCataphractArmor/PrestigeCataphractArmor|
|Royalty|Apparel_ArmorHelmetCataphractPrestige|Overhead|FullHead|Things/Pawn/Humanlike/Apparel/PrestigeCataphractHelmet/PrestigeCataphractHelmet|
|Royalty|Apparel_ArmorLocust|Middle, Shell|Torso, Neck, Shoulders, Arms, Legs|Things/Pawn/Humanlike/Apparel/LocustArmor/LocustArmor|
|Royalty|Apparel_ArmorMarineGrenadier|Middle, Shell|Torso, Neck, Shoulders, Arms, Legs|Things/Pawn/Humanlike/Apparel/GrenadierArmor/GrenadierArmor|
|Royalty|Apparel_ArmorCataphractPhoenix|Middle, Shell|Torso, Neck, Shoulders, Arms, Legs|Things/Pawn/Humanlike/Apparel/PhoenixArmor/PhoenixArmor|
|Royalty|Apparel_Gunlink|Overhead|UpperHead|Things/Pawn/Humanlike/Apparel/Gunlink/Gunlink|
|Royalty|Apparel_PackJump|Belt|Waist|Things/Pawn/Humanlike/Apparel/JumpPack/JumpPack|
|Royalty|Apparel_PackBroadshield|Belt|Waist|Things/Pawn/Humanlike/Apparel/BroadshieldPack/BroadshieldPack|
|Royalty|OrbitalTargeterMechCluster|Belt|Waist|Things/Item/Equipment/WeaponSpecial/OrbitalTargeterMechCluster/OrbitalTargeterMechCluster|
|Core|Apparel_PsychicShockLance|Belt|Waist|Things/Item/Artifact/PsychicShockLance/PsychicShockLance|
|Core|Apparel_PsychicInsanityLance|Belt|Waist|Things/Item/Artifact/PsychicInsanityLance/PsychicInsanityLance|
|Core|Apparel_CowboyHat|Overhead|UpperHead|Things/Pawn/Humanlike/Apparel/CowboyHat/CowboyHat|
|Core|Apparel_BowlerHat|Overhead|UpperHead|Things/Pawn/Humanlike/Apparel/BowlerHat/BowlerHat|
|Core|Apparel_TribalHeaddress|Overhead|UpperHead|Things/Pawn/Humanlike/Apparel/TribalHeaddress/TribalHeaddress|
|Core|Apparel_Tuque|Overhead|UpperHead|Things/Pawn/Humanlike/Apparel/Tuque/Tuque|
|Core|Apparel_WarMask|Overhead|FullHead|Things/Pawn/Humanlike/Apparel/WarMask/WarMask|
|Core|Apparel_WarVeil|Overhead|FullHead|Things/Pawn/Humanlike/Apparel/Veil/Veil|
|Core|Apparel_SimpleHelmet|Overhead|UpperHead|Things/Pawn/Humanlike/Apparel/SimpleHelmet/SimpleHelmet|
|Core|Apparel_AdvancedHelmet|Overhead|UpperHead|Things/Pawn/Humanlike/Apparel/AdvancedHelmet/AdvancedHelmet|
|Core|Apparel_PowerArmorHelmet|Overhead|FullHead|Things/Pawn/Humanlike/Apparel/PowerArmorHelmet/PowerArmorHelmet|
|Core|Apparel_ArmorHelmetRecon|Overhead|FullHead|Things/Pawn/Humanlike/Apparel/ReconArmorHelmet/ReconHelmet|
|Core|Apparel_PsychicFoilHelmet|Overhead|UpperHead|Things/Pawn/Humanlike/Apparel/PsychicFoilHelmet/PsychicFoilHelmet|
|Core|Apparel_HatHood|Overhead|UpperHead|Things/Pawn/Humanlike/Apparel/Hood/Hood|
|Core|Apparel_ClothMask|Overhead|Mouth|Things/Pawn/Humanlike/Apparel/ClothMask/ClothMask|
|Core|Apparel_TribalA|OnSkin|Torso, Legs|Things/Pawn/Humanlike/Apparel/TribalA/TribalA|
|Core|Apparel_Parka|Shell|Torso, Neck, Shoulders, Arms|Things/Pawn/Humanlike/Apparel/Parka/Parka|
|Core|Apparel_Pants|OnSkin|Legs|—|
|Core|Apparel_BasicShirt|OnSkin|Torso, Shoulders|Things/Pawn/Humanlike/Apparel/ShirtBasic/ShirtBasic|
|Core|Apparel_CollarShirt|OnSkin|Torso, Neck, Shoulders, Arms|Things/Pawn/Humanlike/Apparel/ShirtButton/ShirtButton|
|Core|Apparel_Duster|Shell|Torso, Neck, Shoulders, Arms, Legs|Things/Pawn/Humanlike/Apparel/Duster/Duster|
|Core|Apparel_Jacket|Shell|Torso, Neck, Shoulders, Arms|Things/Pawn/Humanlike/Apparel/Jacket/Jacket|
|Core|Apparel_PlateArmor|Middle, Shell|Torso, Neck, Shoulders, Arms, Legs|Things/Pawn/Humanlike/Apparel/PlateArmor/PlateArmor|
|Core|Apparel_FlakVest|Middle|Torso, Neck|Things/Pawn/Humanlike/Apparel/FlakVest/FlakVest|
|Core|Apparel_FlakPants|OnSkin, Middle|Legs|—|
|Core|Apparel_FlakJacket|Shell|Torso, Neck, Shoulders, Arms|Things/Pawn/Humanlike/Apparel/FlakJacket/FlakJacket|
|Core|Apparel_PowerArmor|Middle, Shell|Torso, Neck, Shoulders, Arms, Legs|Things/Pawn/Humanlike/Apparel/PowerArmor/PowerArmor|
|Core|Apparel_ArmorRecon|Middle, Shell|Torso, Neck, Shoulders, Arms, Legs|Things/Pawn/Humanlike/Apparel/ReconArmor/ReconArmor|
|Core|Apparel_Cape|Shell|Torso, Neck, Shoulders, Arms, Legs|Things/Pawn/Humanlike/Apparel/Cape/Cape|
|Core|Apparel_Robe|Shell|Torso, Shoulders, Arms, Legs|Things/Pawn/Humanlike/Apparel/Robe/Robe|
|Core|Apparel_SmokepopBelt|Belt|Waist|Things/Pawn/Humanlike/Apparel/SmokepopPack/SmokepopPack|
|Core|Apparel_FirefoampopPack|Belt|Waist|Things/Pawn/Humanlike/Apparel/FirefoamPack/FirefoamPack|
|Core|Apparel_ShieldBelt|Belt|Waist|—|
|Core|OrbitalTargeterBombardment|Belt|Waist|Things/Item/Equipment/WeaponSpecial/OrbitalTargeterBombardment/OrbitalTargeterBombardment|
|Core|OrbitalTargeterPowerBeam|Belt|Waist|Things/Item/Equipment/WeaponSpecial/OrbitalTargeterPowerBeam/OrbitalTargeterPowerBeam|
|Core|TornadoGenerator|Belt|Waist|—|
|Odyssey|Apparel_VacsuitHelmet|Overhead|FullHead|Things/Pawn/Humanlike/Apparel/VacsuitHelmet/VacsuitHelmet|
|Odyssey|Apparel_Vacsuit|Middle, Shell|Torso, Neck, Shoulders, Arms, Legs|Things/Pawn/Humanlike/Apparel/Vacsuit/Vacsuit|
|Odyssey|Apparel_VacsuitChildren|Middle, Shell|Torso, Neck, Shoulders, Arms, Legs|Things/Pawn/Humanlike/Apparel/KidVacsuit/KidVacsuit|
|Odyssey|Apparel_PackHunter|Belt|Waist|Things/Pawn/Humanlike/Apparel/HunterDronePack/HunterDronePack|
|Odyssey|Apparel_CerebrexNode|Belt|Waist|Things/Pawn/Humanlike/Apparel/CerebrexNode/CerebrexNodePack|
|Ideology|Apparel_Headwrap|Overhead|UpperHead|Things/Pawn/Humanlike/Apparel/Headwrap/Headwrap|
|Ideology|Apparel_Broadwrap|Overhead|FullHead, Neck, Shoulders|Things/Pawn/Humanlike/Apparel/Broadwrap/Broadwrap|
|Ideology|Apparel_VisageMask|Overhead|FullHead|—|
|Ideology|Apparel_Slicecap|Overhead|UpperHead|—|
|Ideology|Apparel_Collar|Overhead|Neck|Things/Pawn/Humanlike/Apparel/SlaveCollar/SlaveCollar|
|Ideology|Apparel_AuthorityCap|Overhead|UpperHead|Things/Pawn/Humanlike/Apparel/AuthorityCap/AuthorityCap|
|Ideology|Apparel_Tailcap|Overhead|UpperHead|Things/Pawn/Humanlike/Apparel/Tailcap/Tailcap|
|Ideology|Apparel_Shadecone|Overhead|UpperHead|Things/Pawn/Humanlike/Apparel/Shadecone/Shadecone|
|Ideology|Apparel_Flophat|Overhead|UpperHead|Things/Pawn/Humanlike/Apparel/Flophat/Flophat|
|Ideology|Apparel_BodyStrap|Shell|Torso|Things/Pawn/Humanlike/Apparel/BodyStrap/BodyStrap|
|Ideology|Apparel_Burka|Shell|FullHead, UpperHead, Neck, Shoulders, Torso, Legs, Arms|Things/Pawn/Humanlike/Apparel/Burka/Burka|
|Ideology|Apparel_TortureCrown|Overhead|UpperHead|Things/Pawn/Humanlike/Apparel/TortureCrown/TortureCrown|
|Ideology|Apparel_Blindfold|EyeCover|Eyes|Things/Pawn/Humanlike/Apparel/Blindfold/Blindfold|
