import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import japanize_matplotlib
import datetime
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent

def flow_visual(extract_month, axis_visible, correction):
    # データ読み込み
    df = pd.read_excel('C:/Users/nakam/Dropbox/資産/Django/家計データベース.xlsx')
    df = df.iloc[:,:6]
    df = df.sort_values('日付')
    # display(df.head())

    # 目標データ読み込み
    df_T = pd.read_excel('C:/Users/nakam/Dropbox/資産/Django/目標データベース.xlsx')
    df_T['給与目標']=df_T['基本給目標'] + df_T['手当目標'] + df_T['残業代目標']
    df_T =df_T[['year', '基本給目標', '給与目標', '一時金目標', '年収']]
    # display(df_T.head())

    # 支払元が入金以外のデータを集計
    df_temp = df[~(df['支払元']=='入金')]
    df_timeseries = df_temp.groupby('日付').sum()

    # カレンダーを作成し、結合（左上グラフ用データ完成）
    dates_DF = pd.DataFrame(index=pd.date_range(pd.to_datetime('2021-09-23'), pd.to_datetime(datetime.datetime.now()), freq='D'))
    df_timeseries = pd.merge(dates_DF, df_timeseries, how='left', right_index=True, left_index=True)
    df_timeseries = df_timeseries.fillna(0)
    df_timeseries['残金'] = df_timeseries['入出金'].cumsum()
    # display(df_timeseries.head())

    # year(年度)カラムを追加
    df.loc[df['日付'].dt.month >= 4, 'year'] = df['日付'].dt.year
    df.loc[df['日付'].dt.month < 4, 'year'] = df['日付'].dt.year - 1

    # yearカラムをfloat型からint型に変換
    df['year'] = df['year'].astype(int)

    # 月ごとの集計を実行
    df_month = df.copy()
    df_month['月'] = df_month['日付'].dt.strftime('%Y%m')
    df_month = df_month.pivot_table(columns='大区分', index=['月','year'], aggfunc='sum', values='入出金')

    # 毎月の収入の平均を計算
    df_year_temp = df.copy()
    df_year_temp = df_year_temp.pivot_table(columns='大区分', index='year', aggfunc='mean', values='入出金')
    df_year_temp['収入合計'] = df_year_temp['基本給'] + df_year_temp['残業代'] + df_year_temp['手当']
    df_year_temp = df_year_temp.reset_index()
    df_year_temp = df_year_temp[['year','収入合計']]

    # 収入の目標を結合
    df_year_temp = pd.merge(df_year_temp, df_T, how='left',on='year')
    df_year_temp['year'] = df_year_temp['year'].astype('str')
    # display(df_year_temp)

    # 毎月の収支に結合（右上グラフ用データ完成）
    df_month = df_month.reset_index()
    df_month['year'] = df_month['year'].astype('str')
    df_month = pd.merge(df_month, df_year_temp, how='left', on='year')
    df_month['月'] = pd.to_datetime(df_month['月'], format="%Y%m")
    # display(df_month.head())

    # 一時金データ（左下グラフ用データ完成）
    df_bonus = df_month.dropna(subset=['一時金'])
    # display(df_bonus.head())

    # 年毎のデータ作成（右下グラフ用データ完成）
    df_year = df_month.groupby('year').sum()
    df_year = df_year.reset_index()
    df_T['year'] = df_T['year'].astype('str')
    df_year = pd.merge(df_year, df_T[['year','年収']], how='left', on='year')
    # display(df_year)

    # 左上グラフ化
    plt.rcParams['figure.subplot.bottom'] = 0.3
    plt.rcParams['figure.subplot.top'] = 0.95
    plt.subplots_adjust(left=0.1, right=0.95, bottom=0.3, top=0.95)
    plt.figure(figsize=(10, 4))

    plt.fill_between(df_timeseries.index, df_timeseries['残金']/10000*correction, [0])
    plt.tick_params(labelsize=11)
    plt.xticks(rotation=90)
    plt.yticks(fontsize=12)
    plt.ylabel('残金(万円)', fontsize=15)
    plt.grid()

    # 年月日の入力があったときの処理
    if extract_month:
        plt.xlim(extract_month, pd.to_datetime(datetime.datetime.now()))
    # 年月日の入力がないときの処理
    else:
        plt.xlim(pd.to_datetime('2021-09-24'), pd.to_datetime(datetime.datetime.now()))
    plt.savefig(str(BASE_DIR)+'/static/images/flow_visual.png')
    # plt.show()

    # 右上グラフ化
    plt.rcParams['figure.subplot.bottom'] = 0.15
    plt.rcParams['figure.subplot.top'] = 0.95
    plt.figure(figsize=(10,4.0))

    plt.stackplot(df_month['月'], df_month['基本給']/10000*correction, df_month['残業代']/10000*correction, df_month['手当']/10000*correction, labels=['基本給','残業代','手当'])
    plt.stackplot(df_month['月'], -df_month['税金']/10000*correction, -df_month['保険']/10000, labels=['税金','保険'], alpha=0.7)
    plt.plot(df_month['月'], df_month['収入合計']/10000*correction, linewidth=3, c='red', label='年度平均')
    plt.plot(df_month['月'], df_month['基本給目標']/10000*correction, linewidth=3, c='black', label='基本給目標', linestyle=':')
    plt.plot(df_month['月'], df_month['給与目標']/10000*correction, linewidth=3, c='black', label='収入目標', linestyle='--')

    plt.legend(loc='upper left', fontsize=8)
    plt.tick_params(labelsize=11)
    plt.yticks(fontsize=12)
    plt.ylabel('入出金(万円)', fontsize=15)
    plt.xticks(rotation=90)

    # 軸消しの場合
    if not axis_visible:
        plt.yticks(color="None")
        plt.tick_params(length=0)
    else:
        plt.grid()
    plt.savefig(str(BASE_DIR)+'/static/images/income_visual.png')
    # plt.show()

    # 左下グラフ化
    plt.rcParams['figure.subplot.bottom'] = 0.2
    plt.rcParams['figure.subplot.top'] = 0.95
    plt.figure(figsize=(10,3.0))
    plt.stackplot(df_bonus['月'], df_bonus['一時金']/10000*correction, labels=['一時金'])
    plt.stackplot(df_bonus['月'], df_bonus['一時金税金']/10000*correction, labels=['税金'], alpha=0.5)
    plt.plot(df_bonus['月'], df_bonus['一時金目標']/10000/2*correction, label='目標', color='red', linewidth=3, linestyle=':')
    plt.legend(loc='upper left',fontsize=11)
    plt.tick_params(labelsize=11)
    plt.yticks(fontsize=12)
    plt.ylabel('入出金(万円)',fontsize=15)
    plt.xticks(rotation=90)

    # 軸消しの場合
    if not axis_visible:
        plt.yticks(color="None")
        plt.tick_params(length=0)
    else:
        plt.grid()
    plt.savefig(str(BASE_DIR)+'/static/images/income_visual_bonus.png')
    # plt.show()

    # 右下グラフ化
    plt.rcParams['figure.subplot.bottom'] = 0.2
    plt.rcParams['figure.subplot.top'] = 0.95
    plt.figure(figsize=(10,3.0))
    plt.stackplot(df_year['year'], df_year['基本給']/10000*correction, (df_year['手当'] + df_year['残業代'])/10000*correction,
                df_year['一時金']/10000, labels=['基本給','残業代+手当','一時金'])
    plt.plot(df_year['year'], df_year['年収_y']/10000*correction, label='目標', color='red', linewidth=3, linestyle=':')
    plt.legend(loc='upper left', fontsize=8)
    plt.tick_params(labelsize=11)
    plt.yticks(fontsize=12)
    plt.ylabel('入出金(万円)', fontsize=15)
    plt.xticks(rotation=90)

    # 軸消しの場合
    if not axis_visible:
        plt.yticks(color="None")
        plt.tick_params(length=0)
    else:
        plt.grid()

    plt.savefig(str(BASE_DIR)+'/static/images/income_visual_annual.png')
    # plt.show()
