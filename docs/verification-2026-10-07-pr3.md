# PR #3 レビュー修正の検証（2026-10-07）

対象は公開PR #3の `d1a2c5d5ad1886b75d83ae7b37c5b49e2b2f3cb3` に本修正を加えたチェックアウト。未公開ローカル実装や過去の試験結果を今回の結果に含めない。

## 修正と静的確認

- 公開範囲をレビュー対象コミットとmainの差分（108ファイル）に合わせ、4資料の注記を統一した。専用ScenarioDefが未収録であることをREADMEの導入手順に明記した。
- 公開の9月24日検証記録の件数は16・26・35件。統合142件・子機41件を公開記録の結果として扱う記述を訂正した。
- 利用版Assembly-CSharp.dllのメタデータで `GeneUtility.ImplantXenogermItem(Pawn pawn, Xenogerm xenogerm)` と `GeneUtility.ReimplantXenogerm(Pawn caster, Pawn recipient)` を確認し、各処理完了後に種族外見を再保証するHarmony Postfixを追加した。マーカーは非遺伝性のxenogeneのまま保持する。
- .NET SDK 8.0.425で `tools/build.sh` と `tools/selftest/build.sh` が成功。どちらも警告0・エラー0。製品DLLも更新した。
- `tools/validate.py --game-data <RimWorldMac.app/Data>`: `PASS: 36 XML files, 20 Defs, 34 transparent PNG files`。`git diff --check`も成功。
- 回帰セルフテストに通常移植後のマーカー復元、体型遺伝子の維持、再移植後のマーカーと種族体型の復元、人間への通常移植/再移植でマーカーを追加しない判定を追加した。最終テストソースはビルド確認済み。

## 隔離ゲーム起動の限界

RimWorld `1.6.4871 rev597`、Core/Biotech/Harmony/VEF/Caelavi/一時セルフテストMODを指定し、専用Modsディレクトリと新しい `-savedatafolder` で起動した。通常のModsリンク・設定・セーブは変更していない。

`tools/selftest/run.py --game-app <隔離RimWorldMac.app> --output-dir <新規ケース> --seconds 240 --skip-build` を実行。ログに保存先隔離の確認と `[Caelavi] Alpha assembly loaded.` があり、抽出エラーは0件だったが、画面は `Generating map...` のまま進まず、セルフテストのSTART/RESULT行がないまま240秒で終了した。ランナー終了コードは1、結果は `MISSING`。ゲーム内回帰テスト・保存再読込は未実施であり、PASSとは扱わない。自動追加DLCを含む実ロード構成も記録される段階に到達していない。

テスト後に人間Pawnの生成を既存の関係生成なしヘルパーへ揃え、テストDLLを再ビルドした。この最終版のゲーム内判定も未実施。移植直後の描画、通常手術、自然出生、別プロセスの保存再読込は今後の実機確認対象。

## SHA-256

| ファイル | SHA-256 |
|---|---|
| 更新した `1.6/Assemblies/Caelavi.dll` | `aaeff918fee86138c5030478da41aebf1391357dbc412188ef992b1b5108247f` |
| 参照 `Assembly-CSharp.dll` | `6d06b881d59cb54d05b674e8631fa2e8b1629dc8b8dd294a5bcc928f1e5d2148` |
| 参照 `0Harmony.dll` | `353daafec180bb8e7bbe4da78f2a7cdc78067392e3a4e79dc8e7af295f2371e6` |
| 参照 `VEF.dll` | `2f0c890c54dd0498aebcfa42b63a859f8acee894adddd08807a523d683e8dc6d` |

参照DLLは開発機のゲーム・Workshopから読み取ったもので、リポジトリに同梱しない。
