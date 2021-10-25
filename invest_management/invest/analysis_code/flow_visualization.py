import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import japanize_matplotlib
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent

def flow_visual():
    df = pd.read_excel('C:/Users/nakam/Dropbox/資産/Django/家計データベース.xlsx')
    df = df.iloc[:,:6]

    df = df.sort_values('日付')

    df_T = pd.read_excel('C:/Users/nakam/Dropbox/資産/Django/目標データベース.xlsx')
    df_T['給与目標']=df_T['基本給目標']+df_T['手当目標']+df_T['残業代目標']
    df_T =df_T[['year','基本給目標','給与目標','一時金目標','年収']]

    # カレンダーを作成し結合
    dates_DF = pd.DataFrame(index=pd.date_range(pd.to_datetime('2021-09-23'), df['日付'].max(), freq='D'))

    df_temp = df[~(df['支払元']=='入金')]
    df_timeseries = df_temp.groupby('日付').sum()

    df_timeseries = pd.merge(dates_DF, df_timeseries, how='left',right_index=True, left_index=True)
    df_timeseries = df_timeseries.fillna(0)
    df_timeseries['残金'] = df_timeseries['入出金'].cumsum()
    df_timeseries ['日付文字列'] = df_timeseries.index.strftime('%Y-%m-%d')

    plt.rcParams['figure.subplot.bottom'] = 0.3
    plt.rcParams['figure.subplot.top'] = 0.95
    plt.figure(figsize=(10,4))
    plt.fill_between(df_timeseries.index,df_timeseries['残金'],[0])
    plt.subplots_adjust(left=0.1, right=0.95, bottom=0.3, top=0.95)
    plt.xticks(rotation = 90)
    plt.ylabel('残金(円)')
    plt.grid()
    plt.tick_params(labelsize=11)
    plt.savefig(str(BASE_DIR)+'/static/images/flow_visual.png')


    # year(年度)カラムを追加
    df.loc[df['日付'].dt.month >= 4, 'year'] = df['日付'].dt.year
    df.loc[df['日付'].dt.month < 4, 'year'] = df['日付'].dt.year - 1

    # yearカラムをfloat型からint型に変換
    df['year'] = df['year'].astype(int)

    temp = df.copy()
    temp['月'] = temp['日付'].dt.strftime('%Y%m')
    temp = temp.pivot_table(columns='大区分',index=['月','year'],aggfunc='sum',values='入出金')

    temp_year =  df.copy()
    temp_year = temp_year.pivot_table(columns='大区分',index='year',aggfunc='mean',values='入出金')
    temp_year['収入合計']=temp_year['基本給']+temp_year['残業代']+temp_year['手当']
    temp_year = temp_year.reset_index()
    temp_year = temp_year[['year','収入合計']]

    temp_year = pd.merge(temp_year,df_T,how='left',on='year')
    temp_year['year']=temp_year['year'].astype('str')

    temp=temp.reset_index()
    temp['year'] = temp['year'].astype('str')
    temp = pd.merge(temp,temp_year,how='left', on='year')
    temp['月'] = pd.to_datetime(temp['月'],format="%Y%m")

    plt.rcParams['figure.subplot.bottom'] = 0.15
    plt.rcParams['figure.subplot.top'] = 0.95
    plt.figure(figsize=(10,4.0))

    plt.stackplot(temp['月'], temp['基本給']/10000,temp['残業代']/10000,temp['手当']/10000,labels=['基本給','残業代','手当'])
    plt.stackplot(temp['月'], -temp['税金']/10000,-temp['保険']/10000,labels=['税金','保険'],alpha=0.7)
    plt.plot(temp['月'], temp['収入合計']/10000,linewidth=3, c='red', label='年度平均')
    plt.plot(temp['月'], temp['基本給目標']/10000,linewidth=3, c='black', label='基本給目標',linestyle=':')
    plt.plot(temp['月'], temp['給与目標']/10000,linewidth=3, c='black', label='収入目標',linestyle='--')

    plt.legend(loc='upper left',fontsize=8)
    plt.tick_params(labelsize=11)
    plt.yticks(fontsize=12)
    plt.ylabel('入出金(万円)',fontsize=15)
    plt.grid()
    plt.tick_params(labelsize=11)
    
    plt.xticks(rotation=90)
    plt.savefig(str(BASE_DIR)+'/static/images/income_visual.png')

    temp_bonus = temp.dropna(subset=['一時金'])

    plt.rcParams['figure.subplot.bottom'] = 0.2
    plt.rcParams['figure.subplot.top'] = 0.95
    plt.figure(figsize=(10,3.0))
    plt.stackplot(temp_bonus['月'], temp_bonus['一時金']/10000,labels=['一時金'])
    plt.stackplot(temp_bonus['月'], temp_bonus['一時金税金']/10000,labels=['税金'],alpha=0.5)
    plt.plot(temp_bonus['月'], temp_bonus['一時金目標']/10000/2, color='red',linewidth=3,linestyle=':')
    plt.legend(loc='upper left',fontsize=11)
    plt.tick_params(labelsize=11)
    plt.yticks(fontsize=12)
    plt.ylabel('入出金(万円)',fontsize=15)
    plt.grid()

    plt.xticks(rotation=90)
    plt.savefig(str(BASE_DIR)+'/static/images/income_visual_bonus.png')


    temp_yeargraph = temp.groupby('year').sum()
    temp_yeargraph = temp_yeargraph.reset_index()

    df_T['year']=df_T['year'].astype('str')

    temp_yeargraph=pd.merge(temp_yeargraph, df_T[['year','年収']], how='left' ,on='year')
    plt.rcParams['figure.subplot.bottom'] = 0.2
    plt.rcParams['figure.subplot.top'] = 0.95
    plt.figure(figsize=(10,3.0))
    plt.stackplot(temp_yeargraph['year'], temp_yeargraph['基本給']/10000,(temp_yeargraph['手当']+temp_yeargraph['残業代'])/10000,
                temp_yeargraph['一時金']/10000,labels=['基本給','残業代+手当','一時金'])
    plt.plot(temp_yeargraph['year'], temp_yeargraph['年収_y']/10000, color='red',linewidth=3,linestyle=':')
    plt.legend(loc='upper left',fontsize=8)
    plt.tick_params(labelsize=11)
    plt.yticks(fontsize=12)
    plt.ylabel('入出金(万円)',fontsize=15)
    plt.grid()
    
    plt.xticks(rotation=90)
    plt.savefig(str(BASE_DIR)+'/static/images/income_visual_annual.png')
