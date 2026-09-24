# 隔離実機セルフテスト

`tools/selftest/Mod` は配布しない一時MOD。`tools/package.py` の配布対象に `tools/` は含まれない。自己テストの`GameComponent`は `-quicktest -caelavi-selftest` の両フラグで始めた新規ゲームで一度だけ走る。通常プレイや既存セーブのロードでは発火しない。

RimWorld 1.6 のCore `QuickStarter.CheckQuickStart()` は `-quicktest` でPlayシーンを開き、`Root_Play.SetupForQuickTestPlay()` が小さな新規世界とCrashlanded開始マップを生成する。Core `Game.InitNewGame()` はマップ初期化後に `GameComponentUtility.StartedNewGame()` を呼ぶ。この時点で `PawnGenerator.GeneratePawn` に必要なGame/World/Factionが存在する。

```sh
DOTNET_BIN=/tmp/caelavi-dotnet/dotnet sh tools/build.sh
DOTNET_BIN=/tmp/caelavi-dotnet/dotnet python3 tools/selftest/run.py --hide-conflicting-symlink
```

実行前に本体MODをビルドする。ランナーはテストDLLだけを`tools/selftest/Mod/Assemblies`にビルドし、既存のゲームが動作中なら起動しない。Core/Biotech/Harmony/VEF、本体MOD、セルフテストMODのみを一時ModsConfigへ記入し、各MODをゲームのModsフォルダに実行中だけsymlinkする。ゲーム側は有効な他DLCを自動追加するため、実際の構成はPlayer.logの`Initializing new game with mods`で確認する。`--hide-conflicting-symlink`は旧RIM/Caelaviのsymlinkに限って実行中だけ退避し、終了時に戻す。`-savedatafolder`が隔離先として認識されたログを確認できなければゲームを止める。

結果は新規の一時ディレクトリに`manifest.json`、`Player.log`、`selftest-results.txt`、`errors.txt`として残る。既定の上限は600秒で、`[CaelaviSelfTest] RESULT`が出れば早く終了する。`--seconds`と`--output-dir`で変更できる。テストは`CA_DevelopmentPawn`を実際に生成し、成人年齢、専用種族、左右翼、外見Gene、飛行Comp、手動展翼、2翼/1翼/0翼のHediff、試作翼ガード、12歳時の飛行不可をログへ記録する。さらに生成した母・父とBiotechの妊娠Hediffから6日分の`TickInterval`を呼び、産卵数と卵ごとの父母参照を調べる。孵化は各卵を12日目の最後のtickへ一時的に進め、実際の`CompTick`孵化処理と3歳の子を確認する。実時間の12日間運用は対象外。生成Pawnはテスト用の隔離ゲーム内だけに存在し、配布MODや通常セーブには残さない。

孵化確認後、別に生成した展翼中のPawn、進行度を12,345 tickへ置いた未孵化卵と両親、保留中の特派員`ChoiceLetter`を隔離`SaveData/Saves`へ`GameDataSaveLoader.SaveGame`で保存する。Coreの起動イベントが終わってから`LoadGame`を予約し、`GameComponent.LoadedGame`で同一Thing ID、展翼Hediff段階、卵の進行度と父母参照、選択レターの対象マップと選択肢を確認する。`GameComponent`の保存欄でテスト対象IDを引き継ぎ、ロード前オブジェクトへの参照を判定に使わない。長時間の孵化、自然な受精経路、特派員の実イベント発火・受諾は別の確認が必要。

静的ビルドやDefロードだけではPASSにならない。`RESULT PASS`と`errors.txt`空の両方をランナーの成功条件とする。ゲームの起動・世界生成に失敗した場合は未実施/失敗としてログを確認する。

## 2026-09-24 の隔離実行

- RimWorld `1.6.4871 rev597`。Player.logの実ロード順はHarmony、Core、Royalty、Ideology、Biotech、Anomaly、Odyssey、VEF、Caelavi、Caelavi SelfTest。`-quicktest`はメニューを経ず新規マップを生成した。
- 出力: `/var/folders/rd/gx3846jj5yzg6w6xr3mn2kph0000gn/T/caelavi-selftest-d9691df55c7b/`。`[Caelavi] Alpha assembly loaded.`、`RESULT PASS passed=26 failures=0`、抽出エラー0。実行後に一時symlinkと旧symlinkを復元した。
- 18歳の開発用Pawn、左右翼、外見Gene、手動展翼、2/1/0翼のHediff、翼ガード着脱、12歳の年齢制限、共和国勢力の生成とgoodwill 0のNeutralを確認した。
- 生成した母親の妊娠Hediffを6日分進めると卵が2個出現した。各卵が独立し、父母参照を持った。各卵を孵化直前へ進めると3歳児が2名生成され、外見Geneと両親との関係を確認した。卵数1と3の抽選、継続した12日間の温度管理、保存再読込、自然の受精経路は今回検証していない。

## 2026-09-24 の保存再読込追加確認

- 出力: `/var/folders/rd/gx3846jj5yzg6w6xr3mn2kph0000gn/T/caelavi-selftest-7064ba18bba6/`。`RESULT PASS passed=35 failures=0`、抽出エラー0、ランナー終了コード0。隔離先に`CaelaviSelfTest-SaveReload.rws`を作成し、同じ起動中にロードした。終了時は一時symlinkを復元した。
- ロード後、保存前に展翼した18歳Pawnの展翼状態・翼2枚・飛行Hediff第2段階、未孵化卵の進行度12,345 tick・両親と`CompHasPawnSources`の参照、保留中の特派員レターと対象マップ・3つの選択肢を確認した。旧孵化テストの父親もマップへ登録してから保存し、子の親関係ロードエラーを回避した。
- 追加の反復では、ゲーム初期化前の`UIRoot_Play.UIRootOnGUI`に断続的なNullReferenceExceptionが4件出たため、`RESULT PASS`でもランナーは終了コード1になった。出力は`/var/folders/rd/gx3846jj5yzg6w6xr3mn2kph0000gn/T/caelavi-selftest-4ba63ec905c5/`。原因未特定であり、上記のエラー0の実行結果と区別する。
- 別の反復`/var/folders/rd/gx3846jj5yzg6w6xr3mn2kph0000gn/T/caelavi-selftest-c8ed2ae75b25/`は保存・ロード後の35件の判定を通過したが、quicktestが生成したバニラHumanの親`Thing_Human1050`が保存されず、ロード時に参照エラー1件を出してランナーは失敗した。卵の父母IDとは異なる。
- このHuman親をテスト世界の`WorldPawns`へ登録する対処を試作してビルドした。`/var/folders/rd/gx3846jj5yzg6w6xr3mn2kph0000gn/T/caelavi-selftest-8690c48e5150/`はMODロードからquicktestの新規ゲーム開始へ進まず240秒でタイムアウトした。抽出エラー0でも結果行がないため失敗扱い。対処は実行されず効果を確認できなかったため、検証済みコードへ戻した。
