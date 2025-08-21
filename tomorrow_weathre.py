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

# ライブラリのインポート
import xgboost as xgb
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

if __name__ == '__main__':
   print("--- XGBoostモデルの学習を開始します ---")

scale_pos_weight = 11
if __name__ == '__main__':
   print(f"ポジティブクラスの重み (scale_pos_weight): {scale_pos_weight:.2f}")

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