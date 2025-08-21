import requests as re ,json,datetime as dt,pandas as pd

''' 現在位置情報(IPアドレス)から今の天気をスクレイピング、明日の天気をAIの予測から5段階表示 '''
'''
▼▼
get_ip_address
現在地のIPアドレスを取得する

get_ip_location
取得したIPアドレスを元に緯度経度を取得する

get_weather
取得した緯度経度から現在位置の天気を情報を取得する
△△
'''


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
    
# 取得したIPアドレスから大まかな現在位置を表示
def Get_Location_About():
    x = get_ip_location()
    url_lo_api = f'https://mreversegeocoder.gsi.go.jp/reverse-geocoder/LonLatToAddress?lat={x['lat']}&lon={x['lon']}'
    res = re.get(url_lo_api)
    res.raise_for_status()
    gla = res.json()
    gla = gla.get('results')
    gla = gla.get('lv01Nm')
    return gla


#  緯度と経度から現在の天気情報を取得する（APIキー不要)
def get_weather(lat, lon):
    try:
        url_api = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&timezone=Asia/Tokyo'
        response = re.get(url_api)
        response.raise_for_status()
        weather_data = response.json()
        # print(weather_data)
        weather_data_2 = weather_data.get('current_weather_units')
        # print(weather_data_2)
        weather_data_3 = weather_data.get('current_weather')
        # print(weather_data_3)
        return {
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
            'weathercode':weather_data_3.get('weathercode'),}
            
    except re.exceptions.RequestException as e:
        print(f"天気情報の取得中にエラーが発生しました: {e}")
        return None
    
 # WMOコードで見る天気予報の一覧(0~99で表記)
wmo_weather_codes = {
      0: "快晴",
      1: "主に晴",
      2: "部分的に曇り",
      3: "曇り",
      4: "煙、火山の噴煙",
      5: "もや",
      6: "塵や砂塵が\n広範囲に浮遊している",
      7: "塵や砂塵を巻き上げる",
      8: "はっきりと発達した塵旋風",
      9: "塵や砂塵を\n巻き上げた状態の突風",
      10: "はっきりしているが、\n継続的ではないもや",
      11: "地面がはっきりしているが、\n継続的ではないもや",
      12: "雷鳴が聞こえるが、降水がない",
      13: "積乱雲がはっきりと見える",
      14: "はっきりと見えるが、\n継続的ではない稲妻",
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

def tenki():
   #  変数をグローバル化しているため取り扱い注意
    global x_lat,x_lon
    # global kaze,hukou,tenko,x_lat,x_lon,weather_code_now

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
       if __name__ == '__main__':
            print(y)

       kaze = f'{y['husoku']}{y['windspeed']}'
      # リスト内包により余分な表記がはいる可能性があるため使用時には hukou[0]として使う 
       hukou = [f'{hukou_dic[v]}' for v in hukou_dic if v <= y['hukou']]
       tenko = [wmo_weather_codes[v] for v in wmo_weather_codes if v == y['weathercode']]
       kion = f'{y['kion']}{y['seshi']}'
       weather_code_now = y['weathercode']

      #  5分ごとに更新する(koshin_kirikae:更新切り替えボタンで停止も可能)
    #    if koushin_btn_active == True:
    #       root.after(3000000,tenki)
       
    except Exception as e:
        print(f'エラーが発生しました{e}')
        pass    
    return kaze,hukou[0],tenko[0],kion,x_lat,x_lon,weather_code_now

# print(f'天気は{tenko[0]}\n風速{kaze} {hukou[0]}')

if __name__ == '__main__':
    print(get_ip_address())
    print(get_ip_location())
    print(Get_Location_About())
    print(tenki())