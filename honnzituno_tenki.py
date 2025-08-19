import requests as re ,json,datetime as dt,pandas as pd
import tkinter as tk,tkinter.ttk as ttk

# グローバルipアドレスの取得する
def get_ip_address():
    try:
        response = re.get('https://api.ipify.org?format=json')
        response.raise_for_status()
        ip_data = response.json()
        return ip_data['ip']
    except re.exceptions.RequestException as e:
        print(f"IPアドレスの取得中にエラーが発生しました: {e}")
        return None
    
#  取得したIPアドレスから緯度と経度を取得する
def get_ip_location(genzaiti=get_ip_address()):
    try:
        url = f'http://ip-api.com/json/{genzaiti}?lang=ja'
        response = re.get(url)
        response.raise_for_status()
        location_data = response.json()
        
        if location_data['status'] == 'success':
            return {
               #  lat=緯度
                'lat': location_data.get('lat'),
               #  lon=経度
                'lon': location_data.get('lon'),
               #  city=IPアドレスに属する市町村
                'city': location_data.get('city'),
               #  timezone=IPアドレスの位置情報に基づいて推定されるタイムゾーン
                'timezone': location_data.get('timezone')
            }
        else:
            print(f"位置情報の取得に失敗しました: {location_data.get('message')}")
            return None
            
    except re.exceptions.RequestException as e:
        print(f"位置情報の取得中にエラーが発生しました: {e}")
        return None
    
#  緯度と経度から現在の天気情報を取得する（APIキー不要)
def get_weather(lat, lon):
    try:
        url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&timezone=Asia/Tokyo'
        response = re.get(url)
        response.raise_for_status()
        weather_data = response.json()
        weather_data_2 = weather_data.get('current_weather_units')
        weather_data_3 = weather_data.get('current_weather')
        return {
            # elevation=取得地の標高（メートル）
            'hyoko':weather_data.get('elevation'),
            # temperature=摂氏温度の表記
            'seshi':weather_data_2.get('temperature'),
            # windspeed=風速の表記
            'windspeed':weather_data_2.get('windspeed'),
            # winddirection=風向きの表記
            'winddirection':weather_data_2.get('winddirection'),
            # temperature=現在の気温
            'kion':weather_data_3.get('temperature'),
            # windspeed=現在の風速
            'husoku':weather_data_3.get('windspeed'),
            # winddirection=現在の風向
            'hukou':weather_data_3.get('winddirection'),
            # weathercode=天気コード　例「0」= 快晴
            'weathercode':weather_data_3.get('weathercode')}
    except re.exceptions.RequestException as e:
        print(f"天気情報の取得中にエラーが発生しました: {e}")
        return None

# 画面を更新(5分ごとに)する切り替えボタン関数
koushin_btn_active = True
def koushin_kirikae():
    global koushin_btn_active
   #  現在の状態を反転させる
    koushin_btn_active = not koushin_btn_active

def tenki():
   #  変数をグローバル化しているため取り扱い注意
    global hyoko,kaze,hukou,tenko
    # WMOコードで見る天気予報の一覧(0~99で表記)
    wmo_weather_codes = {
      0: "快晴",
      1: "主に晴れ",
      2: "部分的に曇り",
      3: "曇り",
      4: "煙、火山の噴煙",
      5: "もや",
      6: "塵や砂塵が広範囲に浮遊している",
      7: "塵や砂塵を巻き上げる",
      8: "はっきりと発達した塵旋風",
      9: "塵や砂塵を巻き上げた状態の突風",
      10: "はっきりしているが、継続的ではないもや",
      11: "地面がはっきりしているが、継続的ではないもや",
      12: "雷鳴が聞こえるが、降水がない",
      13: "積乱雲がはっきりと見える",
      14: "はっきりと見えるが、継続的ではない稲妻",
      15: "視程内の稲妻",
      16: "視程外の雷雨",
      17: "雷雨",
      18: "風に煽られた降水",
      19: "激しい雹や雪",
      20: "霧雨",
      21: "雨",
      22: "雪",
      23: "みぞれ",
      24: "着氷性の霧雨",
      25: "着氷性の雨",
      26: "着氷性の雪",
      27: "雨を伴う雷雨",
      28: "雪を伴う雷雨",
      29: "雹を伴う雷雨",
      30: "弱い風雨",
      31: "弱い風雨",
      32: "弱い風雨",
      33: "並の風雨",
      34: "強い風雨",
      35: "強い風雨",
      36: "弱い雪",
      37: "弱い雪",
      38: "並の雪",
      39: "強い雪",
      40: "弱い着氷性の霧",
      41: "着氷性の霧",
      42: "弱い着氷性の霧",
      43: "強い着氷性の霧",
      44: "霧",
      45: "霧",
      46: "強い霧",
      47: "強い霧",
      48: "霧氷",
      49: "霧氷",
      50: "弱い霧雨",
      51: "弱い霧雨",
      52: "弱い霧雨",
      53: "並の霧雨",
      54: "強い霧雨",
      55: "強い霧雨",
      56: "弱い着氷性の霧雨",
      57: "強い着氷性の霧雨",
      58: "弱いみぞれ",
      59: "強いみぞれ",
      60: "弱い雨",
      61: "弱い雨",
      62: "並の雨",
      63: "並の雨",
      64: "強い雨",
      65: "強い雨",
      66: "弱い着氷性の雨",
      67: "強い着氷性の雨",
      68: "弱いみぞれ",
      69: "強いみぞれ",
      70: "弱い雪",
      71: "弱い雪",
      72: "並の雪",
      73: "並の雪",
      74: "強い雪",
      75: "強い雪",
      76: "弱い細氷",
      77: "細氷",
      78: "弱い着氷性の雨",
      79: "強い着氷性の雨",
      80: "弱い通り雨",
      81: "通り雨",
      82: "激しい通り雨",
      83: "弱いみぞれの通り雨",
      84: "強いみぞれの通り雨",
      85: "弱い雪の通り雨",
      86: "強い雪の通り雨",
      87: "弱い雹の通り雨",
      88: "強い雹の通り雨",
      89: "弱い着氷性の通り雨",
      90: "強い着氷性の通り雨",
      91: "弱い雨と雷雨",
      92: "並の雨と雷雨",
      93: "弱い雪と雷雨",
      94: "並の雪と雷雨",
      95: "雷雨",
      96: "雷雨と弱い雹",
      97: "雷雨と並の雨",
      98: "雷雨と並の雪",
      99: "雷雨と強い雹"}
   #  風向を東西南北表記するための辞書
    hukou_dic={
      0.0: "北 (N)",
      11.26: "北北東 (NNE)",
      33.76: "北東 (NE)",
      56.26: "東北東 (ENE)",
      78.76: "東 (E)",
      101.26: "東南東 (ESE)",
      123.76: "南東 (SE)",
      146.26: "南南東 (SSE)",
      168.76: "南 (S)",
      191.26: "南南西 (SSW)",
      213.76: "南西 (SW)",
      236.26: "西南西 (WSW)",
      258.76: "西 (W)",
      281.26: "西北西 (WNW)",
      303.76: "北西 (NW)",
      326.26: "北北西 (NNW)",
      348.76: "北 (N)"}

    try:
       x = get_ip_location()
       x_lat = x['lat']
       x_lon = x['lon']
       y = get_weather(x_lat,x_lon)

       hyoko = f'{y['hyoko']}m'
       kaze = f'{y['husoku']}{y['windspeed']}'
      # リスト内包により余分な表記がはいる可能性があるため使用時には hukou[0]として使う 
       hukou = [f'{hukou_dic[v]}' for v in hukou_dic if v <= y['hukou']]
       tenko = [wmo_weather_codes[v] for v in wmo_weather_codes if v == y['weathercode']]
      #  5分ごとに更新する(koshin_kirikae:更新切り替えボタンで停止も可能)
       '''
       if koushin_btn_active == True:
          root.after(3000000,tenki)
       '''
    except:
        pass    

# tenki()
# print(f'現在の標高は{hyoko}\n天気は{tenko[0]}\n風速{kaze} {hukou[0]}')

# 過去のデータを取り扱うためのインポート
from meteostat import Point,Hourly

# データの取得期間を設定
# 可能な限り過去のデータを取得するため、開始日を1970年1月1日に設定
start = dt.datetime(1970, 1, 1)
end = dt.datetime.now()

# 経度緯度を変数に設定
x = get_ip_location()
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
# print(x_ms.head())
print(y_ms.head())
#欠損値を確認（.isnull()が欠損値を1で返す→そのためsum()で足せば欠損値の総数が分かる）
# print(x_ms.isnull().sum(),y_ms.isnull().sum())
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
print("--- SMOTEでデータバランスを調整中 ---")
# SMOTEを適用して、訓練データをオーバーサンプリング
X_train_resampled, Y_train_resampled = smote.fit_resample(X_train, Y_train)

print(f"調整前: {Y_train.value_counts()}")
print(f"調整後: {Y_train_resampled.value_counts()}")

# 全体から80％抽出した訓練データを学習させる
forest.fit(X_train,Y_train)

'''学習したデータを保存できる
# 学習済みモデルを一時的に保存
# 将来的に同じモデルを再利用する場合に便利です。
from joblib import dump
dump(model, 'weather_prediction_model.joblib')
print("学習済みモデルを 'weather_prediction_model.joblib' に保存しました。")
'''

from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
'''コードの解説
model.predict(X_test):

学習済みのモデルmodelに対して、predict()メソッドを呼び出し、**テストデータX_test**を渡します。

このメソッドは、X_testの各行（1時間ごとの気象データ）に対して、「雨が降る（1）」か「雨が降らない（0）」かを予測し、その結果をY_predという変数に格納します。

accuracy_score(Y_test, Y_pred):

**正解率（Accuracy）**を計算する関数です。

予測結果Y_predのうち、実際の正解Y_testと一致した割合を計算します。

confusion_matrix(Y_test, Y_pred):

混同行列と呼ばれる表を出力します。これは、モデルがどのような間違いをしたのかを分かりやすく示してくれます。

classification_report(Y_test, Y_pred):

分類レポートを出力します。これは、正解率だけでなく、より詳細な評価指標（precision、recall、f1-scoreなど）を分かりやすくまとめてくれます。

このステップを実行することで、あなたが構築したモデルが、未知のデータに対してどの程度の予測能力を持つかを客観的に評価できます。

実行後の結果について
このコードを実行すると、コンソールにaccuracyやconfusion_matrixの結果が表示されます。

accuracyが1.0に近いほど、モデルは正確です。

もし結果が期待に沿わない場合は、特徴量（x_ms）の見直しや、モデルのパラメータ調整（例：n_estimatorsを増やす）といった改善を試みることができます。
'''
print("--- モデルの評価を開始します ---")

# 1. テストデータで予測を実行
# predict() メソッドが予測を実行する
Y_pred = forest.predict(X_test)

# 2. モデルの精度（正解率）を計算
accuracy = accuracy_score(Y_test, Y_pred)
print(f"モデルの精度（Accuracy）: {accuracy:.4f}")

# 3. 混同行列（Confusion Matrix）で予測結果を詳細に分析
print("\n--- 混同行列（Confusion Matrix） ---")
print(confusion_matrix(Y_test, Y_pred))

# 4. 分類レポートでさらに詳細な評価を確認
print("\n--- 分類レポート（Classification Report） ---")
print(classification_report(Y_test, Y_pred))
'''
precision (適合率)	モデルが「雨が降る」と予測したケースのうち、実際に雨が降った割合。	誤って「雨が降る」と予測するミスを減らしたい場合。<br>（例: 雨予報を信じて外出を取りやめたが、実際は晴れだった）
recall (再現率)	実際に雨が降ったケースのうち、モデルが正しく「雨が降る」と予測できた割合。	雨が降るケースを見逃すミスを減らしたい場合。<br>（例: 雨予報を見逃して傘を持たずに外出したら、雨に降られた）
f1-score	precisionとrecallのバランスを表す指標。	両方の指標をバランスよく高めたい場合。
'''

print("--- モデルの評価が完了しました ---")

# ライブラリのインポート
import xgboost as xgb

print("--- XGBoostモデルの学習を開始します ---")
''' 要素が重く雨が降らない結果の破損値が多きため調整
# クラスの不均衡を考慮するための重みを計算
# 雨が降らない（0）ケースの数 ÷ 雨が降る（1）ケースの数
# この比率を scale_pos_weight に設定
positive_class_count = (Y_train == 1).sum()
negative_class_count = (Y_train == 0).sum()
scale_pos_weight = negative_class_count / positive_class_count
'''
scale_pos_weight = 10
print(f"ポジティブクラスの重み (scale_pos_weight): {scale_pos_weight:.2f}")

# XGBoostモデルを初期化
# objective='binary:logistic': 二値分類を指定
# eval_metric='logloss': 評価指標を指定
# use_label_encoder=False: 将来のバージョンの警告を避けるため
# scale_pos_weight: クラスの不均衡を補正する重み
model_xgb = xgb.XGBClassifier(
    objective='binary:logistic',
    eval_metric='logloss',
    use_label_encoder=False,
    n_estimators=150,
    learning_rate=0.1,
    scale_pos_weight=scale_pos_weight,
    random_state=42
)

# 訓練データを使ってモデルを学習させる
model_xgb.fit(X_train, Y_train)

print("--- XGBoostモデルの学習が完了しました ---")

# 予測を実行
Y_pred_xgb = model_xgb.predict(X_test)

# モデルの評価
print("\n--- 分類レポート（Classification Report） ---")
print(classification_report(Y_test, Y_pred_xgb))