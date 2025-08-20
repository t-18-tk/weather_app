import tkinter as tk
# from PIL import Image, ImageTk #画像を読み込むため
import today_weather as tw,tomorrow_weathre as tmw

# 明日の天気を予測する
# tomorrow_weatherがAI学習で重いため関数内で処理
def tomorrow_wether_yosoku():
    global lbl_tomorrow
    x = tmw.Tomorrow_tenkiyosoku()
    lbl_tomorrow.config(text=f'明日は{x[0]}\n降水確率は{x[1]}%',
                        font=('Comic Sans MS',8,''))
    pass

''' tkinterで画面に表示 '''

# 天候によって背景を切り換える
def wether_img(self):
    global pt
    imgn = f'{self}.png'
    pt = tk.PhotoImage(file=imgn)
    img_can.create_image(50,0,image=pt,anchor='n')

# 画面を更新(5分ごとに)する切り替えボタンの関数
after_id = None
koushin_btn_active = True
def koushin_kirikae():
    global koushin_btn_active,after_id
   #  現在の状態を反転させる
    koushin_btn_active = not koushin_btn_active
    print(f'更新状況を切り換えました：{koushin_btn_active}')
    if koushin_btn_active:
        koushin_btn.config(text='更新',
                           bg='#2196F3',
                           fg='#ffffff')
        print('更新を開始')
        weather_app()
    else:
        koushin_btn.config(text='停止',
                           bg='#BDBDBD',
                           fg='#555555')
        if after_id:
            root.after_cancel(after_id)
            after_id = None
            print('更新を停止')

# いまの天気を取得する
def weather_app():
    global lbl_tenki,lbl_temperature_wind,after_id
    t_0 = tw.tenki()
    t_1 = f'{t_0[2]}'
    t_2 = f'気温：{t_0[3]}\n風速：{t_0[0]}\n風向：{t_0[1]}'
    lbl_tenki.config(text=f'{t_1}',
                     font=('Comic Sans MS',11,''))
    lbl_temperature_wind.config(text=f'{t_2}',
                                font=('Comic Sans MS',7,''))

    # WMOコードをカテゴリに分類した辞書
    weather_categories = {
      # 晴れ
      "sunny": [0, 1, 2, 3, 4],
      # 曇り
      "cloudy": [44, 45, 46, 47],
      # 雨
      "rainy": [18, 20, 21, 24, 25, 30, 31, 32, 33, 34, 35, 50, 51, 52, 53, 54, 55, 60, 61, 62, 63, 64, 65, 66, 67, 80, 81, 82, 89, 90],
      # 雪・みぞれ・氷
      "snowy": [19, 22, 23, 26, 36, 37, 38, 39, 40, 41, 42, 43, 48, 49, 56, 57, 58, 59, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 83, 84, 85, 86, 87, 88],
      # 雷雨
      "stormy": [12, 13, 14, 15, 16, 17, 27, 28, 29, 91, 92, 93, 94, 95, 96, 97, 98, 99],
   }
    wc = t_0[-1]
    # print(wc)
    wc_br = None
    for v,x in weather_categories.items():
       if wc in x:
          wc_br = v
          print(f'いまの天気は<{wc_br}>')
          wether_img(wc_br)
          lbl_wether.config(text=f'{wc_br}',
                            font=('Comic Sans MS',30,'bold italic'))
          break
    # 中身があるかどうか、またはTureかFalseで判断する
    # この場合Tureなら実行される
    if koushin_btn_active:
        print('5分後に自動更新')
        # .afterは変数に代入される時に一緒に次のタスク予約をするためこの状態でOK
        after_id = root.after(300000,weather_app)

# rootメインの設定
root = tk.Tk()
root.title('weather app')
root.minsize(300,100)

# menubarの設定
menubar = tk.Menu(root)
root.config(menu = menubar)# 設定を変更できる(.config)

# 今日の天気
lbl_wether = tk.Label(text='')
lbl_tenki = tk.Label(text='')
lbl_temperature_wind = tk.Label(text='')

# 更新切り替えボタン
koushin_btn = tk.Button(text='更新',
                        bg='#2196F3',
                        fg='#ffffff',
                        command=koushin_kirikae)

# 画像を表示するためのキャンバス
img_can = tk.Canvas(width=100,
                    height=100,
                    highlightthickness=0)

# 明日の天気予測
lbl_tomorrow = tk.Label(text='')

# pack
img_can.place(relx=0.5, rely=0.05, anchor='ne')
lbl_tenki.place(relx=0.55, rely=0.1, anchor='w')
lbl_temperature_wind.place(relx=0.55, rely=0.3, anchor='w')
lbl_tomorrow.place(relx=0.55, rely=0.5, anchor='w')
koushin_btn.place(relx=0.99, rely=0.99, anchor='se')
lbl_wether.place(relx=0.5, rely=0.9, anchor='s')
weather_app()
tomorrow_wether_yosoku()

root.mainloop()

