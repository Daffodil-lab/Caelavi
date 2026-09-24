# アルファ仮表示素材

**この画像一式はゲーム接続を試すための新規プレースホルダーであり、カエラヴィの正式デザインではない。**
体格、肌色、羽色、翼形、衣装、性差、成長段階を決定する資料として扱わない。

## 収録内容

- `Textures/Caelavi/Pawn/Body_{south,east,north}.png`：胴体
- `Textures/Caelavi/Pawn/Head_{south,east,north}.png`：頭
- `Textures/Caelavi/Pawn/WingLeft_{south,east,north}.png`、`WingRight_*`：左右の収納翼
- `Textures/Caelavi/Pawn/WingLeftDeployed_{south,east,north}.png`、`WingRightDeployed_*`：展翼時の仮表示。飛行Compの手動状態に接続済み
- `Textures/Caelavi/Pawn/Tail_{south,east,north}.png`：尾羽
- `Textures/Caelavi/Pawn/TempleLeft_{south,east,north}.png`、`TempleRight_*`：側頭羽
- `Textures/Caelavi/Pawn/Crest_{south,east,north}.png`：冠羽
- `Textures/Caelavi/UI/GeneMorphology.png`：一時的な外見Geneのアイコン

Pawnパーツは各256×256の透過PNG。`east` は東向きで、`west` は東向きテクスチャの左右反転を想定する。左翼／右翼は**本人の解剖学的な左／右**で命名し、桃色／青色の小さな識別マークを付けた。色は描画と左右の検査用で、採用済みの羽色や肌色ではない。

## 再生成

Python 3 と Pillow 10 以上を用意し、リポジトリ内で次を実行する。

```sh
python3 tools/generate_placeholder_art.py
```

スクリプト内の座標・曲線・図形だけを描画する。既知のCaelavi素材、旧試作、ゲーム本体、他MOD、隣接フォルダの画像やソースは読み込まない。生成は同じ環境で再実行可能であり、出力PNGはリポジトリへ含めるためゲーム導入時にPillowを必要としない。

## 確認範囲

[方向別・収納／展翼プレビュー](placeholder-art-preview.png)は重なりを目視するための合成見本で、実際のPawnRenderTree描画ではない。Headと頭の羽を胴体に対してプレビュー用に56px上げている。左右欠損と展翼の描画条件はコードに接続したが、ゲーム上の描画順、衣服・帽子との重なり、肖像、子供の縮小表示、左右欠損の非表示、展翼切替後の表示は実機で確認する。現在の画像そのものはこれらのゲーム動作を証明しない。
