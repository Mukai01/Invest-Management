import pandas as pd
import matplotlib
matplotlib.use('Agg') # <= これが必要
from matplotlib import pyplot as plt
import japanize_matplotlib
from pathlib import Path
from datetime import datetime, timedelta
BASE_DIR = Path(__file__).resolve().parent.parent.parent

#5桁の数値を日付に変換
def excel_date(num):
    return(datetime(1899, 12, 30) + timedelta(days=num))

def visualization(axis_visible, make_graph):
    # データの読み込み
    df = pd.read_excel('C:/Users/nakam/Dropbox/資産/Django/資産データベース.xlsx')

    # 集計の定義
    category={'現金':['預金','楽天証券','退職金'],
            '財形貯蓄':['財形貯蓄'],
            '持ち株':['MHI','Toyota'],
            '全世界株':['全世界株'],
            '国内株':['国内株','国内投資信託'],
            '先進国株':['先進国投資信託','確定拠出年金'],
            '新興国株':['新興国投資信託'],
            '米国個別株':['米国株'],
            '仮想通貨':['bitflyer']}

    # 円グラフのカテゴリー
    category2={'無リスク資産':['現金','財形貯蓄'],
            'サテライト':['仮想通貨','持ち株','米国個別株'],
            'コア':['全世界株','国内株','先進国株','新興国株'],}

    category3={'全世界':['全世界株'],
            '先進国':['先進国株'],
            '国内':['国内株'],
            '新興国':['新興国株']}

    category4={'仮想通貨':['仮想通貨'],
            '持ち株':['持ち株'],
            '米国個別株':['米国個別株'],
            }

    # 日付に変換
    df['日付'] =df['日付'].apply(excel_date)
    df['日付']=pd.to_datetime(df['日付'])

    # 集計を実行
    df2=df[['日付','預金']].copy()

    # 箱を作成
    for i in category:
        for j in category[i]:
            df2[i]=0

    # df2にデータを格納
    for i in category:
        for j in category[i]:
            df2[i]=df2[i]+df[j]/10000
    del df2['預金']
    # display(df2)


    if make_graph:
        # 可視化
        colorlist = ['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd','#8c564b','#e377c2','#7f7f7f','#bcbd22','#17becf']
        plt.rcParams['figure.subplot.bottom'] = 0.15
        plt.rcParams['figure.subplot.top'] = 0.95

        plt.figure(figsize=(10,4))
        plt.stackplot(df2['日付'],df2['現金'],df2['財形貯蓄'],df2['持ち株'],
                    df2['全世界株'],df2['国内株'],df2['先進国株'],df2['新興国株'],
                    df2['米国個別株'],df2['仮想通貨'],labels=['現金', '財形貯蓄', '持ち株', 
                    '全世界株', '国内株', '先進国株', '新興国株', '米国個別株','仮想通貨'],
                    colors=colorlist)
        plt.plot(df['日付'],df['目標']/10000, color='red',ls='--')

        plt.legend(loc='upper left',fontsize=10)
        plt.ylabel('資産額(万円)',fontsize=15)
        plt.tick_params(labelsize=11)
        plt.xticks(rotation=90)

        # 軸消しの場合
        if not axis_visible:
            plt.yticks(color="None")
            plt.tick_params(length=0)
        else:
            plt.grid()

        plt.savefig(str(BASE_DIR)+'/static/images/asset_timeseries.png')
        # plt.show()

    if make_graph:
        # 無リスク可視化
        plt.rcParams['figure.subplot.bottom'] = 0.15
        plt.rcParams['figure.subplot.top'] = 0.95
        plt.figure(figsize=(10,3.5))

        plt.stackplot(df2['日付'],df2['現金'],df2['財形貯蓄'],labels=['現金', '財形貯蓄'])

        plt.legend(loc='upper left',fontsize=10)
        plt.ylabel('資産額(万円)',fontsize=15)
        plt.tick_params(labelsize=11)
        plt.xticks(rotation=90)

        # 軸消しの場合
        if not axis_visible:
            plt.yticks(color="None")
            plt.tick_params(length=0)
        else:
            plt.grid()

        plt.savefig(str(BASE_DIR)+'/static/images/asset_timeseries_nonrisk.png')
        # plt.show()

    if make_graph:
        # 有リスク可視化
        plt.rcParams['figure.subplot.bottom'] = 0.15
        plt.rcParams['figure.subplot.top'] = 0.95
        plt.figure(figsize=(10,3.5))

        plt.stackplot(df2['日付'],df2['持ち株'],df2['全世界株'],df2['国内株'],df2['先進国株'],df2['新興国株'],
                    df2['米国個別株'],df2['仮想通貨'],labels=['持ち株', 
                    '全世界株', '国内株', '先進国株', '新興国株', '米国個別株','仮想通貨'],
                    colors=colorlist[2:])

        plt.legend(loc='upper left',fontsize=10)
        plt.ylabel('資産額(万円)',fontsize=15)
        plt.tick_params(labelsize=11)
        plt.xticks(rotation=90)

        # 軸消しの場合
        if not axis_visible:
            plt.yticks(color="None")
            plt.tick_params(length=0)
        else:
            plt.grid()

        plt.savefig(str(BASE_DIR)+'/static/images/asset_timeseries_risk.png')
        # plt.show()

    # 円グラフ可視化
    df3 = df2.dropna().tail(1)

    label_list = []
    value_list = []

    for i in category2:
        value = 0
        for j in category2[i]:
            value = value + df3[j].values[0]
        value_list.append(value)
        label_list.append(i)

    if make_graph:
        plt.rcParams['font.size'] = 17.0
        plt.rcParams['figure.subplot.bottom'] = 0.1
        plt.rcParams['figure.subplot.top'] = 0.9
        plt.figure(figsize=(5,4)) 
        plt.title("【全資産】",fontsize = 22) 
        plt.pie(value_list,labels=label_list,autopct="%1.1f%%")
        plt.savefig(str(BASE_DIR)+'/static/images/asset_portfolio.png')
        # plt.show()

    # コア資産可視化
    label_list = []
    value_list = []

    for i in category3:
        value = 0
        for j in category3[i]:
            value = value + df3[j].values[0]
        value_list.append(value)
        label_list.append(i)

    if make_graph:
        plt.rcParams['font.size'] = 17.0
        plt.rcParams['figure.subplot.bottom'] = 0.1
        plt.rcParams['figure.subplot.top'] = 0.9
        plt.figure(figsize=(5,4)) 
        plt.title("【コア資産】",fontsize = 22) 
        plt.pie(value_list,labels=label_list,autopct="%1.1f%%")
        plt.savefig(str(BASE_DIR)+'/static/images/asset_portfolio_core.png')
        # plt.show()

    developed_rate = value_list[1]/(value_list[1]+value_list[2]+value_list[3])
    japan_rate = value_list[2]/(value_list[1]+value_list[2]+value_list[3])
    developing_rate = value_list[3]/(value_list[1]+value_list[2]+value_list[3])

    # サテライト資産可視化
    label_list = []
    value_list = []

    for i in category4:
        value = 0
        for j in category4[i]:
            value = value + df3[j].values[0]
        value_list.append(value)
        label_list.append(i)

    if make_graph:
        plt.rcParams['font.size'] = 17.0
        plt.rcParams['figure.subplot.bottom'] = 0.1
        plt.rcParams['figure.subplot.top'] = 0.9
        plt.figure(figsize=(5,4)) 
        plt.title("【サテライト資産】",fontsize = 22) 
        plt.pie(value_list,labels=label_list,autopct="%1.1f%%")
        plt.savefig(str(BASE_DIR)+'/static/images/asset_portfolio_sattelite.png')
        # plt.show()

    return developed_rate, japan_rate, developing_rate