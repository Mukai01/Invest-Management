from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
from django_pandas.io import read_frame
import pandas as pd
from datetime import date,timedelta
import matplotlib.pyplot as plt
import japanize_matplotlib
import calendar

# 最終日を取得する関数
def get_last_date(dt):
    return dt.replace(day=calendar.monthrange(dt.year, dt.month)[1])

def make_invest_timeseries(df):
    # 型の変更
    df['invest_date'] = pd.to_datetime(df['invest_date'])

    # もし今日よりも最終日の月末が後だったら最終日の日付を使用する
    if get_last_date(df['invest_date'].max()) >= date.today():
        last_date = df['invest_date'].max()
    else:
        last_date = get_last_date(df['invest_date'].max())

    # カレンダーを作成し結合
    dates_DF = pd.DataFrame(index=pd.date_range(df['invest_date'].min()-timedelta(days=1), last_date, freq='D'))
    df=df.set_index('invest_date')
    df=pd.merge(dates_DF,df,how='left',right_index=True, left_index=True)

    # 欠損値処理
    df = df.fillna(0)
    df=df.reset_index()

    # 集計
    df2 = df.groupby('index').sum()

    # 累計を計算、単位変更
    for i in df2.columns:
        df2[i] = df2[i].cumsum()
        df2[i] = df2[i]/10000
        
    # 可視化
    plt.rcParams['figure.subplot.bottom'] = 0.3
    plt.rcParams['figure.subplot.top'] = 0.95
    plt.figure(figsize=(10,3.3))

    plt.stackplot(df2.index,df2['all_invest'],df2['developed_invest'],df2['topix_invest'],df2['developing_invest'],labels=['全世界','先進国','日本','新興国'])
    plt.legend(loc='upper left')
    plt.xticks(rotation=90, fontsize=10)
    plt.yticks(fontsize=12)
    plt.ylabel('投資額(万円)',fontsize=15)
    plt.grid()
    plt.savefig(str(BASE_DIR)+'/static/images/invest_timeseries.png')

    # 基準価額の可視化
    plt.rcParams['figure.subplot.bottom'] = 0.3
    plt.rcParams['figure.subplot.top'] = 1
    plt.figure(figsize=(10,3.5))

    stock_list=['all_price', 'developed_price', 'topix_price', 'developing_price']
    name_dic={'all_price':'全世界', 'developed_price': '先進国', 'topix_price':'日本', 'developing_price':'新興国'}
    for i in stock_list:
        temp = df.loc[df[i]>0,['index', i]]
        plt.plot(temp['index'], temp[i], label = name_dic[i])

    plt.legend(loc='upper left')
    plt.xticks(rotation=90, fontsize=11)
    plt.yticks(fontsize=12)
    plt.ylabel('基準価額',fontsize=15)
    plt.grid()
    plt.savefig(str(BASE_DIR)+'/static/images/price_timeseries.png')