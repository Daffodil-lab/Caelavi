# アルファ版の検証記録（2026-09-24）

この文書は、このリポジトリで新たに作ったMODの検証だけを記録する。旧試作のテスト結果は含めない。「静的検査」「ゲームのロード」「ゲーム内の動作」「保存と再読込」を別の結果として扱う。

## 独立ロード検証の準備

`tools/run_smoke.py` は、macOSのRimWorld 1.6インストールを検出し、Core、Biotech、Harmony、Vanilla Expanded Framework（VEF）の `About.xml` と packageId を確認する。Harmony は、この環境にあるVEFの必須依存として含める。`-savedatafolder` に新規の隔離ディレクトリを指定し、そこへ最小構成の `Config/ModsConfig.xml`、`Player.log`、エラー抽出結果を置く。通常のセーブと `ModsConfig.xml` は変更しない。

今回のMODは実行中だけゲームの `Mods` にsymlinkを作る。既存の同一packageIdは検出して起動を拒否する。現在の開発機には旧 `RIM/Caelavi` への `Caelavi-Development` symlink があるため、実機起動時には `--hide-conflicting-symlink` を指定する。このオプションは旧 `RIM/Caelavi` を指すsymlinkにだけ働き、実行中は隔離ディレクトリへ退避し、終了時に復元する。他のディレクトリやsymlinkは変更しない。異常終了で復元されなかった場合は、隔離ディレクトリの `hidden-legacy-link-*` を元のゲーム `Mods` に戻す。

```sh
python3 tools/run_smoke.py
python3 tools/run_smoke.py --run --hide-conflicting-symlink --seconds 180
```

最初のコマンドは環境確認と隔離 `ModsConfig.xml` の作成のみで、ゲームを起動しない。2つ目は既存のRimWorldプロセスがないことを確認してから起動し、指定時間後に終了する。別の場所にゲームまたは前提MODがある場合は `--game-app`、`--vef-dir`、`--harmony-dir` を指定できる。`--output-dir` は未作成のパスだけを受け付ける。

スクリプトは `Player.log` の `Save data folder overridden to ...` を確認できなければゲームを止める。`errors.txt` は `error`、`exception`、Def参照失敗などの行と直後のスタックを抽出する。Steam外から直接起動した際のSteam API警告、Monoのライブラリ探索ログ、Unity終了時のメモリ統計は既知のホスト出力として抽出から除く。抽出件数がゼロでも、メニュー到達、生成、描画、セーブとロードを証明したことにはならない。ゲーム画面と対象操作を別途確認し、この文書へ結果を追記する。

## 現在の状態

| 確認項目 | 状態 | 根拠・次の確認 |
|---|---|---|
| ゲーム・前提MODの検出 | 済 | 手元の `RimWorldMac.app` 1.6、Core、Biotech、Harmony、VEFのpackageIdを確認。VEFのSteam Workshop IDは `2023507013`、Harmonyは `2009463077`。 |
| 隔離設定の生成 | 済 | `tools/run_smoke.py` の準備モードで新規 `ModsConfig.xml` を生成。 |
| ゲーム起動とDefロード | 一部確認 | 隔離起動で実行版 `1.6.4871 rev597`、`[Caelavi] Alpha assembly loaded.`、メインメニューを確認。保存可能な特派員レター追加後のビルドでも下記セルフテストが新規マップへ到達し、抽出エラー0件。 |
| 開発用Pawnの生成と四方向描画 | 一部確認 | 実ゲーム内で成人・子供のPawnを生成し、種族・年齢・共通Geneを確認。四方向・衣服・睡眠時表示の目視は未確認。 |
| 飛行・翼左右・衣服の被覆 | 一部確認 | 実Pawnの左右翼、2/1/0翼の展翼状態とHediff段階、翼ガード着脱による抑制・復帰、12歳の年齢制限を自動検査。両翼展翼状態の保存再読込も確認。描画、ほかの衣服、片翼状態の再読込は未確認。 |
| 卵・親子関係・再読込 | 一部確認 | 実ゲーム内で6日妊娠Hediff終了、個別卵の産卵、父母参照、12日の最終tickでの孵化、3歳・親子関係を自動検査。未孵化卵の孵化進行度と父母参照の保存再読込も確認。長期経過と自然受精は未確認。 |
| 共和国勢力 | 一部確認 | 新規世界で勢力が生成され、プレイヤーとの関係Neutral・goodwill 0を確認。集落・商人・部隊編成は未確認。 |
| 特派員の加入レター | 一部確認 | `ChoiceLetter` を保留したまま保存再読込し、対象マップ・PawnKind・選択肢が残ることを確認。自然発火と受諾・拒否の操作は未確認。 |

ロード検証には、実行時のゲーム版、DLC、前提MOD、実装コミット、隔離ディレクトリ、結果を対応させて追記する。ゲームのDLLや他MODの素材をこのリポジトリへコピーしない。

### 2026-09-24 初回ロード観測

- 対象: 隔離設定でCore、Biotech、Harmony、VEF、Caelaviを指定。`tools/run_smoke.py --run --hide-conflicting-symlink --seconds 180` を使用。実行時はこのブランチが未コミットであり、飛行と卵生の実装前。
- 隔離ログ: `/var/folders/rd/gx3846jj5yzg6w6xr3mn2kph0000gn/T/caelavi-smoke-5b7b0f5242d1/Player.log`。`-savedatafolder` がその配下の `SaveData` を使ったことをログで確認し、旧symlinkも復元された。
- `Player.log` にCaelaviアセンブリのロードを確認。Steam APIの警告とUnity終了時の統計以外に、Caelavi/Def/Harmony由来のエラー行は見つからなかった。これは生成やゲーム内操作の検証ではない。

### 2026-09-24 二回目の隔離ロード

- 対象: 左右翼・飛行・卵生・民主共和国・義翼までのビルドの一時コピー。翼ガードと特派員イベントは、このコピーの作成後に追加したため含まない。隔離設定ではCore、Biotech、Harmony、VEF、Caelaviを指定した。
- `tools/run_smoke.py --run --hide-conflicting-symlink --seconds 300 --mod-dir <一時コピー>` を実行。隔離先は `/var/folders/rd/gx3846jj5yzg6w6xr3mn2kph0000gn/T/caelavi-smoke-b4b6629195f8/`。実行時版は `1.6.4871 rev597`。
- `-savedatafolder` の隔離をログで確認し、メインメニュー到達を画面で確認。`[Caelavi] Alpha assembly loaded.` があり、`errors.txt` は0件で終了コード0。旧 `Caelavi-Development` symlinkは終了時に復元された。
- 新規コロニー画面の操作は、この自動操作環境で安定しなかったためPawnを生成していない。翼・卵・勢力のゲーム内動作、セーブ・ロードはこの実行からは確認できない。

### 2026-09-24 新規マップでの自動セルフテスト

- 対象: 最新の翼ガード・特派員イベントを含むビルドと、配布ZIPには含めない `tools/selftest` の一時テストMOD。隔離 `ModsConfig.xml` にはHarmony、Core、Biotech、VEF、Caelavi、セルフテストMODを指定した。実際のログの起動MOD列には、ゲーム側が追加したRoyalty、Ideology、Anomaly、Odysseyも含まれる。実行版は `1.6.4871 rev597`。`-quicktest -caelavi-selftest` で新規マップを作り、通常の保存先とは別の `/var/folders/rd/gx3846jj5yzg6w6xr3mn2kph0000gn/T/caelavi-selftest-558db8bdedc1/SaveData` を使用した。
- `Player.log` は同じ隔離ディレクトリに保存。`[Caelavi] Alpha assembly loaded.` と `[CaelaviSelfTest] RESULT PASS passed=16 failures=0` を確認し、抽出エラーは0件。終了後は旧開発用symlinkが復元された。
- 実際に成人18歳と子供12歳の開発用Pawnを生成した。独立種族、共通外見Gene、左右別の翼、飛行Compを確認。手動切替を呼び、両翼・片翼・両翼欠損に対応する飛行Hediff、翼ガード着用中の抑制と脱衣後の復帰、12歳の展翼不可を確認した。これは実Pawnを使った状態・Defの検査であり、四方向表示、経路速度、セーブ再読込、産卵・孵化、勢力や特派員の自然発生は未確認。

### 2026-09-24 卵・共和国を含む二回目のセルフテスト

- 隔離先は `/var/folders/rd/gx3846jj5yzg6w6xr3mn2kph0000gn/T/caelavi-selftest-d9691df55c7b/`。上記と同じ構成で新規マップへ進んだ。特派員の選択付きレター追加後のDLLをロードした。`[CaelaviSelfTest] RESULT PASS passed=26 failures=0`、`errors.txt` は0バイト。ゲームを終了し、旧開発用symlinkの復元を確認した。
- 最初の16項目に加え、新規世界に `CA_DemocraticRepublic` があり、プレイヤーとの関係はNeutral・goodwill 0だった。成人の父母を生成して6日分の妊娠Hediffを進めると、今回の抽選では卵2個が個別に置かれ、各卵に父母参照が残った。各卵の孵化進行を12日直前へ進めて実際の最終 `CompTick` を呼ぶと、2体の3歳の子が生まれ、共通Geneと父母のParent関係を持った。
- 卵を12日間連続で通常tickさせたわけではない。卵とレターの保存再読込、母親が人間の場合の通常出産、外見の目視、事件の自然発火は別途確認する。

### 2026-09-24 保存再読込の隔離セルフテスト

- 成功した実行の隔離先は `/var/folders/rd/gx3846jj5yzg6w6xr3mn2kph0000gn/T/caelavi-selftest-7064ba18bba6/`。新規マップを作り、`SaveData/Saves/CaelaviSelfTest-SaveReload.rws` へ保存して、同じ実行内でそのファイルをロードした。`[CaelaviSelfTest] RESULT PASS passed=35 failures=0`、`errors.txt` は0バイト、ランナー終了コード0。通常のセーブ領域は使っていない。
- ロード後に、両翼展翼中のPawnと段階2の飛行Hediff、未孵化卵の進行度12,345 tick・父母の参照・`CompHasPawnSources`、受諾待ちの特派員 `ChoiceLetter` と対象マップ・PawnKind・3選択肢を確認した。これは保存再読込の一経路の検査であり、自然受精、12日間の通常孵化、受諾と拒否の操作、片翼状態、通常プレイでの長期安定性まで示すものではない。
- 後続のランナー再実行には不安定さがあった。`4ba63ec905c5` は新規ゲーム初期化前に `UIRoot_Play` の例外4件、`c8ed2ae75b25` は自動生成されたHumanの親参照1件がロード時に未解決、`8690c48e5150` は新規ゲーム初期化へ進まず240秒で時間切れとなった。これらはエラー0件の実行として扱わない。最初の成功と後続の失敗を合わせて、クイックテスト環境に再現性の限界があると記録する。
