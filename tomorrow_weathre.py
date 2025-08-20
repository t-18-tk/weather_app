'''
取得した緯度経度から、1970/1/1から本日までの気象データを取得して、雨が　降ってない/降った：0/1　に振り分ける
振り分けたデータと下記データを参考にAIに学習させる
temp	気温 (Temperature)	℃	
rhum	相対湿度 (Relative Humidity)	%	
wspd	風速 (Wind Speed)	km/h	平均風速です。
wdir	風向 (Wind Direction)	°	0〜360度の角度で、風が吹いてくる方角を示します。北が0度です。
pres	気圧 (Pressure)	hPa	
coco	天候コード (Weather Code)	-	雲量を示すのではなく、「晴れ」「曇り」「雨」などの天候を数値で表したコードです。

▼▼
Tomorrow_tenkiyosoku
学習させたデータから明日の天気を5分割("快晴","ほぼ晴れ","時々雨","雨","大雨")と降水確率(%)として引数を返す
△△
'''
import requests as re ,json,datetime as dt,pandas as pd,today_weather as tw


# 過去のデータを取り扱うためのインポート
from meteostat import Point,Hourly

print('---位置情報から天気の変動を学習---')

# データの取得期間を設定
# 可能な限り過去のデータを取得するため、開始日を1970年1月1日に設定
start = dt.datetime(1970, 1, 1)
end = dt.datetime.now()

# 経度緯度を変数に設定
x = tw.get_ip_location()
# print(x)
now_location = Point(x['lat'],x['lon'])

# データを取得する
# MeteostatのAPIが呼び出される
date_api = Hourly(now_location,start,end)

# データを統一した表記に変換（ノットをkm/hに変換するように）
date_api = date_api.normalize()

# データを取得しDataFrameとして格納(pandasのDataFrameという表形式のデータ構造に変換)
date_api = date_api.fetch()
# print(date_api.head()) # 確認用　最初の5行のデータを返す（引数指定で行数変更可能）
'''
temp	気温 (Temperature)	℃	
dwpt	露点 (Dew Point)	℃	空気中の水蒸気が凝結して露を結ぶ温度。湿度の目安になります。
rhum	相対湿度 (Relative Humidity)	%	
prcp	降水量 (Precipitation)	mm	1時間ごとの降水量です。
snow	積雪量 (Snowfall)	mm	降雪量を表します。
wdir	風向 (Wind Direction)	°	0〜360度の角度で、風が吹いてくる方角を示します。北が0度です。
wspd	風速 (Wind Speed)	km/h	平均風速です。
wpgt	最大瞬間風速 (Peak Gust)	km/h	
pres	気圧 (Pressure)	hPa	
tsun	日照時間 (Sunshine)	分	1時間あたりの日照時間です。
coco	天候コード (Weather Code)	-	雲量を示すのではなく、「晴れ」「曇り」「雨」などの天候を数値で表したコードです。
'''
# ffill()でも埋まらない欠損値を雨が降らなかった(0)としてみなす
date_pan = date_api.ffill()
date_pan = date_pan.fillna(0)
# print(date_pan.head(-5))# 再度確認

x_ms = date_pan[['temp','rhum','wspd','wdir','pres','coco']].copy()
y_ms = date_pan[['prcp']].copy()
y_ms['rain'] = y_ms['prcp'] > 0 # 0より大きい場合はrainにTrueで返す
y_ms['rain'] = y_ms['rain'].astype(int) # True/Falseを1/0で返す
y_ms = y_ms.drop(columns = ['prcp'])
if __name__ == '__main__':
   # print(x_ms.head())
   print(y_ms.head())
#欠損値を確認（.isnull()が欠損値を1で返す→そのためsum()で足せば欠損値の総数が分かる）
# print(x_ms.isnull().sum(),y_ms.isnull().sum())
if __name__ == '__main__':
   print(y_ms['rain'].sum())

# データを[過学習]をさけるために80％と20％にわける
from sklearn.model_selection import train_test_split
# 特徴量（X）と目的変数（Y）を定義
X = x_ms
Y = y_ms['rain']

# 訓練データとテストデータに分割
# test_size=0.2 は、テストデータを全体の20%に設定
'''過学習とは
モデルにすべてのデータを与えて学習させてしまうと、そのデータに対する答えは完璧になりますが、
初めて見るデータに対してはうまく予測できない可能性があります。
これを**過学習（overfitting）**と呼びます。

過学習を防ぎ、モデルの汎用性を評価するために、以下の手順でデータを分割します。

訓練データ（Training Data）: モデルの学習に使われるデータです。全体の約80%を使用するのが一般的です。

テストデータ（Test Data）: 学習には一切使わず、モデルが完成した後に最終的な性能を評価するためだけに使うデータです。
全体の約20%を使用します。
'''
# random_state=42 は、毎回同じ結果になるように乱数の種を固定
'''geminiによるrandom_state=42の説明

承知いたしました。random_state=42 について、詳しく説明します。

これは、Scikit-learnや多くの機械学習ライブラリで使われる、**乱数の種（Seed）**を指定するための引数です。

乱数と random_state
コンピュータのプログラムで使われる「乱数」は、実は完全にランダム（予測不可能）ではありません。これは、**「疑似乱数」**と呼ばれ、ある特定の開始点（これを「種」と呼びます）から、決まった計算手順で生成される数列です。

もし種が同じであれば、生成される乱数の数列は毎回同じになります。

random_state=42は、その乱数の種を「42」という固定の数値に設定することを意味しています。

なぜ random_state を使うのか？
機械学習のプロセスには、乱数が使われる場面がいくつかあります。

データの分割 (train_test_split): データを訓練用とテスト用にランダムにシャッフルして分割します。

モデルの初期化: ランダムフォレストのように、初期のパラメータをランダムに設定するモデルがあります。

もしrandom_stateを指定しないと、これらのランダムなプロセスがコードを実行するたびに異なる結果を生み出してしまいます。

例えば、train_test_splitでrandom_stateを指定しない場合、

1回目に実行したときは、たまたまテストデータに「珍しい豪雨のデータ」が多く含まれる。

2回目に実行したときは、テストデータに「晴れの日」が多く含まれる。

ということが起こり、これでは実行するたびにモデルの精度が変わってしまい、結果を比較したり、他の人にコードを共有したりすることが難しくなります。

結論
random_state=42 を指定する主な理由は、コードの再現性（Reproducibility）を確保するためです。

誰がいつ実行しても、まったく同じ結果が得られることを保証します。

モデルの改善（パラメータ調整など）を行う際に、その改善が「偶然」によるものなのか、「本質的な変更」によるものなのかを正確に判断できます。

「42」という数字自体に特別な意味はなく、慣習として使われていることが多いです（映画「銀河ヒッチハイク・ガイド」で「生命、宇宙、そして万物についての究極の疑問の答え」が42だったことに由来すると言われています）。もちろん、他の整数（例：0や123）を指定しても構いません。

重要なのは、**「乱数を使う処理には、必ず同じ random_state を指定する」**ということです。
'''
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

from sklearn.ensemble import RandomForestClassifier as RFC
# ランダムフォレストモデルを初期化
forest = RFC(n_estimators=150, random_state=42)# n_estimators: 作成する決定木の数。多いほど高精度だが計算量が増える。 random_state: 結果を再現可能にするための乱数の種。

# データの精度が悪いために調整
from imblearn.over_sampling import SMOTE
# SMOTEを初期化
smote = SMOTE(random_state=42)
if __name__ == '__main__':
   print("--- SMOTEでデータバランスを調整中 ---")
# SMOTEを適用して、訓練データをオーバーサンプリング
X_train_resampled, Y_train_resampled = smote.fit_resample(X_train, Y_train)

if __name__ == '__main__':
   print(f"調整前: {Y_train.value_counts()}")
   print(f"調整後: {Y_train_resampled.value_counts()}")

        # # 全体から80％抽出した訓練データを学習させる
        # forest.fit(X_train,Y_train)

        # '''学習したデータを保存できる
        # # 学習済みモデルを一時的に保存
        # # 将来的に同じモデルを再利用する場合に便利です。
        # from joblib import dump
        # dump(model, 'weather_prediction_model.joblib')
        # print("学習済みモデルを 'weather_prediction_model.joblib' に保存しました。")
        # '''

        # from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
        # '''コードの解説
        # model.predict(X_test):

        # 学習済みのモデルmodelに対して、predict()メソッドを呼び出し、**テストデータX_test**を渡します。

        # このメソッドは、X_testの各行（1時間ごとの気象データ）に対して、「雨が降る（1）」か「雨が降らない（0）」かを予測し、その結果をY_predという変数に格納します。

        # accuracy_score(Y_test, Y_pred):

        # **正解率（Accuracy）**を計算する関数です。

        # 予測結果Y_predのうち、実際の正解Y_testと一致した割合を計算します。

        # confusion_matrix(Y_test, Y_pred):

        # 混同行列と呼ばれる表を出力します。これは、モデルがどのような間違いをしたのかを分かりやすく示してくれます。

        # classification_report(Y_test, Y_pred):

        # 分類レポートを出力します。これは、正解率だけでなく、より詳細な評価指標（precision、recall、f1-scoreなど）を分かりやすくまとめてくれます。

        # このステップを実行することで、あなたが構築したモデルが、未知のデータに対してどの程度の予測能力を持つかを客観的に評価できます。

        # 実行後の結果について
        # このコードを実行すると、コンソールにaccuracyやconfusion_matrixの結果が表示されます。

        # accuracyが1.0に近いほど、モデルは正確です。

        # もし結果が期待に沿わない場合は、特徴量（x_ms）の見直しや、モデルのパラメータ調整（例：n_estimatorsを増やす）といった改善を試みることができます。
        # '''
        # print("--- モデルの評価を開始します ---")

        # # 1. テストデータで予測を実行
        # # predict() メソッドが予測を実行する
        # Y_pred = forest.predict(X_test)

        # # 2. モデルの精度（正解率）を計算
        # accuracy = accuracy_score(Y_test, Y_pred)
        # print(f"モデルの精度（Accuracy）: {accuracy:.4f}")

        # # 3. 混同行列（Confusion Matrix）で予測結果を詳細に分析
        # print("\n--- 混同行列（Confusion Matrix） ---")
        # print(confusion_matrix(Y_test, Y_pred))

        # # 4. 分類レポートでさらに詳細な評価を確認
        # print("\n--- 分類レポート（Classification Report） ---")
        # print(classification_report(Y_test, Y_pred))
        # '''
        # precision (適合率)	モデルが「雨が降る」と予測したケースのうち、実際に雨が降った割合。	誤って「雨が降る」と予測するミスを減らしたい場合。<br>（例: 雨予報を信じて外出を取りやめたが、実際は晴れだった）
        # recall (再現率)	実際に雨が降ったケースのうち、モデルが正しく「雨が降る」と予測できた割合。	雨が降るケースを見逃すミスを減らしたい場合。<br>（例: 雨予報を見逃して傘を持たずに外出したら、雨に降られた）
        # f1-score	precisionとrecallのバランスを表す指標。	両方の指標をバランスよく高めたい場合。
        # '''

        # print("--- モデルの評価が完了しました ---")

# ライブラリのインポート
import xgboost as xgb
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

if __name__ == '__main__':
   print("--- XGBoostモデルの学習を開始します ---")
''' 要素が重く雨が降らない結果の破損値が多きため調整
# クラスの不均衡を考慮するための重みを計算
# 雨が降らない（0）ケースの数 ÷ 雨が降る（1）ケースの数
# この比率を scale_pos_weight に設定
positive_class_count = (Y_train == 1).sum()
negative_class_count = (Y_train == 0).sum()
scale_pos_weight = negative_class_count / positive_class_count
'''
scale_pos_weight = 11
if __name__ == '__main__':
   print(f"ポジティブクラスの重み (scale_pos_weight): {scale_pos_weight:.2f}")

# XGBoostモデルを初期化
# objective='binary:logistic': 二値分類を指定
# eval_metric='logloss': 評価指標を指定
# scale_pos_weight: クラスの不均衡を補正する重み
model_xgb = xgb.XGBClassifier(
    objective='binary:logistic',
    eval_metric='logloss',
    n_estimators=150,
    learning_rate=0.1,
    scale_pos_weight=scale_pos_weight,
    random_state=42
)

# 訓練データを使ってモデルを学習させる
model_xgb.fit(X_train, Y_train)

if __name__ == '__main__':
   print("--- XGBoostモデルの学習が完了しました ---")

# 予測を実行
Y_pred_xgb = model_xgb.predict(X_test)

# モデルの評価
if __name__ == '__main__':
   print("\n--- 分類レポート（Classification Report） ---")
   print(classification_report(Y_test, Y_pred_xgb))

url = f'https://api.open-meteo.com/v1/forecast?latitude={x['lat']}&longitude={x['lon']}&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,surface_pressure,weather_code&timezone=Asia/Tokyo'
response = re.get(url)
response.raise_for_status()
weather_ai_or = response.json()
weather_ai = pd.DataFrame(weather_ai_or['hourly'])
weather_ai['time'] = pd.to_datetime(weather_ai['time'])
if __name__ == '__main__':
   print(weather_ai)

x_yosoku = weather_ai[['temperature_2m','relative_humidity_2m','wind_speed_10m','wind_direction_10m','surface_pressure','weather_code']].copy()
x_yosoku.columns = ['temp','rhum','wspd','wdir','pres','coco']

''' AI予測に必要な要素
x_ms = date_pan[['temp','rhum','wspd','wdir','pres','coco']].copy()
temp	気温 (Temperature)	℃	
rhum	相対湿度 (Relative Humidity)	%	
wspd	風速 (Wind Speed)	km/h	平均風速です。
wdir	風向 (Wind Direction)	°	0〜360度の角度で、風が吹いてくる方角を示します。北が0度です。
pres	気圧 (Pressure)	hPa	
coco	天候コード (Weather Code)	-	雲量を示すのではなく、「晴れ」「曇り」「雨」などの天候を数値で表したコードです。
'''

print('---学習完了---')

def Tomorrow_tenkiyosoku():
    Y_tomorrow_weather = model_xgb.predict(x_yosoku)
    # print(Y_tomorrow_weather)
    y_sum = Y_tomorrow_weather.sum()
    # print(y_sum)
    y_ps = y_sum / len(Y_tomorrow_weather)
    # print(y_ps)
    rain_labels = {
        0.05:"快晴",        # 0% ～ 5%
        0.15:"ほぼ晴れ",   # 5% ～ 15%
        0.35:"時々雨",     # 15% ～ 35%
        0.65:"雨",         # 35% ～ 65%
        1.0:"大雨"         # 65% ～ 100%
    }
    rain_labels_y = [rain_labels[v] for v in rain_labels if v > y_ps]
    if __name__ == '__main__':
       print(f'明日は{rain_labels_y[0]} 降水確率は{y_ps*100:.1f}%')
    return rain_labels_y[0],f'{y_ps*100:.1f}'