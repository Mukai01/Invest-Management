import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from sklearn.model_selection import GridSearchCV
import mglearn
import numpy as np
import japanize_matplotlib
import numpy as np
from urllib import request
from bs4 import BeautifulSoup
import re
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent

shiller_url = "https://www.multpl.com/shiller-pe"
per_url = 'https://www.multpl.com/s-p-500-pe-ratio'

def get_per(url):
    # shiller-perのスクレイピング
    # html取得
    response = request.urlopen(url)
    content = response.read()
    response.close()
    html = content.decode()
    #print(html)

    # htmlから要素を抽出
    soup = BeautifulSoup(html)
    current_item = soup.find('div', id='current')
    current_item=current_item.get_text()

    # 正規表現で抽出
    p = re.compile('\d+\.\d+')
    shiller_per_value = float(p.search(current_item).group())
    return shiller_per_value

def random_forest_predict_byshillerper(afteryears):
    # データ読み込み
    df=pd.read_excel('C:/Users/nakam/Dropbox/資産/Django/data/S and P PE Ratio.xlsx')
    df1=pd.read_excel('C:/Users/nakam/Dropbox/資産/Django/data/S and P PE Ratio.xlsx', sheet_name='Shiller PE Ratio')
    df2=pd.read_excel('C:/Users/nakam/Dropbox/資産/Django/data/S and P PE Ratio.xlsx', sheet_name='Stock Price')

    # monthの作成
    df1['DateTime'] = pd.to_datetime(df1['DateTime'])
    df1['Month']=df1['DateTime'].dt.strftime('%Y%m')

    df2['DateTime'] = pd.to_datetime(df2['DateTime'])
    df2['Month']=df2['DateTime'].dt.strftime('%Y%m')

    df = df.iloc[:,:2]
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    df['Month']=df['DateTime'].dt.strftime('%Y%m')

    # 結合
    df3=pd.merge(df2,df,how='left',on='Month')
    df3=pd.merge(df3,df1,how='left',on='Month')
    df3=df3.sort_values('DateTime_x')
    df3=df3.reset_index(drop=True)
    # display(df3)

    # 数年後のリターンを計算
    df3['afteryears']=0
    for i in range(len(df3)):
        now_month = df3.loc[i, 'Month']
        after_month = str(int(now_month)+afteryears*100)
        # print(now_month,"⇒",after_month)

        try :
            # print(df3[df3['Month']==after_month]['S&P 500'].values[0])
            df3.loc[i,"afteryears"] = df3[df3['Month']==after_month]['S&P 500'].values[0]
        except IndexError:
            continue

    # 数年後リターンの計算
    df3['afteryearsReturn'] = df3['afteryears'] / df3["S&P 500"]

    # リターンが0以外のもののみ抽出
    df4=df3[df3['afteryearsReturn']!=0]
    df4=df4[df4['DateTime_x']>pd.to_datetime('1980-01-01')]
    df4=df4.reset_index(drop=True)
    # display(df4)

    # 学習用データの作成
    x_train = df4['Shiller PE Ratio'].values
    y_train = df4['afteryearsReturn'].values
    x_train = x_train.reshape(-1,1)

    # # GridSearchでパラメータ決定
    # param_grid = {'n_estimators': [1,2,3,4,5,6,7,8,9,10], 'max_depth': [1,2,3,4,5,6,7,8,9,10]}
    # grid_search = GridSearchCV(RandomForestRegressor(), param_grid, cv=5, verbose = 2)
    # grid_search.fit(x_train,y_train)

    # # ヒートマップの作成
    # results = pd.DataFrame(grid_search.cv_results_)
    # scores = np.array(results.mean_test_score).reshape(10, 10)
    # mglearn.tools.heatmap(scores, xlabel='n_estimators', xticklabels=param_grid['n_estimators'],
    #                   ylabel='max_depth', yticklabels=param_grid['max_depth'], cmap="viridis", fmt='%0.1f')
    # plt.show()
        
    # ランダムフォレストによる予測
    rfr = RandomForestRegressor(n_estimators=8,max_depth = 3, random_state=5)
    rfr.fit(x_train,y_train)
    x_test = np.linspace(8,50,1000).reshape(-1,1)
    predict = rfr.predict(x_test)

    # 現在のPerを計算に使用する
    shiller_per_value = get_per(shiller_url)
    now_value=np.array(shiller_per_value).reshape(-1,1)
    estimate=rfr.predict(now_value)

    # グラフ化
    plt.rcParams["legend.framealpha"] = 1
    plt.rcParams['figure.subplot.bottom'] = 0.15
    plt.rcParams['figure.subplot.top'] = 0.90
    plt.figure(figsize=(10,3.5))

    plt.scatter(df4['Shiller PE Ratio'],df4['afteryearsReturn'],s=100,alpha=0.2, label='Since 1980/01/01')
    plt.vlines([shiller_per_value],0.5,df4['afteryearsReturn'].max(),color='black', label='Current Shiller PE Ratio')
    plt.hlines([1],0,50,color='black',linestyles='dotted')
    plt.plot(x_test[:,0],predict,c='r',label='Predict by RandomForest')
    plt.text(now_value+1,df4['afteryearsReturn'].max()/2,'Shiller PER =' + str(shiller_per_value) +'\npredict ='+str(round(estimate[0],2)),fontsize=13)
    plt.xlim([0,50])
    plt.legend(fontsize=12)
    plt.title('{}年後のリターン予測'.format(afteryears),fontsize=18)
    plt.xlabel('Shiller PE ratio',fontsize=15)
    plt.ylabel('{}年後のリターン(倍)'.format(afteryears),fontsize=15)
    plt.xticks(fontsize=11)
    plt.yticks(fontsize=12)
    plt.grid()
    plt.savefig(str(BASE_DIR)+'/static/images/shiller_per_predict.png')
    # plt.show()

def random_forest_predict_byper(afteryears):
    # データ読み込み
    df=pd.read_excel('C:/Users/nakam/Dropbox/資産/Django/data/S and P PE Ratio.xlsx')
    df1=pd.read_excel('C:/Users/nakam/Dropbox/資産/Django/data/S and P PE Ratio.xlsx', sheet_name='PE Ratio')
    df2=pd.read_excel('C:/Users/nakam/Dropbox/資産/Django/data/S and P PE Ratio.xlsx', sheet_name='Stock Price')

    # monthの作成
    df1['DateTime'] = pd.to_datetime(df1['DateTime'])
    df1['Month']=df1['DateTime'].dt.strftime('%Y%m')

    df2['DateTime'] = pd.to_datetime(df2['DateTime'])
    df2['Month']=df2['DateTime'].dt.strftime('%Y%m')

    df = df.iloc[:,:2]
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    df['Month']=df['DateTime'].dt.strftime('%Y%m')

    # 結合
    df3=pd.merge(df2,df,how='left',on='Month')
    df3=pd.merge(df3,df1,how='left',on='Month')
    df3=df3.sort_values('DateTime_x')
    df3=df3.reset_index(drop=True)

    # 5年後のリターンを計算
    df3['afteryears']=0
    for i in range(len(df3)):
        now_month = df3.loc[i, 'Month']
        after_month = str(int(now_month)+afteryears*100)
        # print(now_month,"⇒",after_month)

        try :
            # print(df3[df3['Month']==after_month]['S&P 500'].values[0])
            df3.loc[i,"afteryears"] = df3[df3['Month']==after_month]['S&P 500'].values[0]
        except IndexError:
            continue

    # 数年後リターンの計算
    df3['afteryearsReturn'] = df3['afteryears'] / df3["S&P 500"]

    # リターンが0以外のもののみ抽出
    df4=df3[df3['afteryearsReturn']!=0]
    df4=df4[df4['DateTime_x']>pd.to_datetime('1980-01-01')]
    df4=df4.reset_index(drop=True)
    # display(df4)

    # 学習用データの作成
    x_train = df4['PE Ratio_x'].values
    y_train = df4['afteryearsReturn'].values
    x_train = x_train.reshape(-1,1)

    #     # GridSearchでパラメータ決定
    #     param_grid = {'n_estimators': [1,2,3,4,5,6,7,8,9,10], 'max_depth': [1,2,3,4,5,6,7,8,9,10]}
    #     grid_search = GridSearchCV(RandomForestRegressor(), param_grid, cv=5, verbose = 2)
    #     grid_search.fit(x_train,y_train)

    #     # ヒートマップの作成
    #     results = pd.DataFrame(grid_search.cv_results_)
    #     scores = np.array(results.mean_test_score).reshape(10, 10)
    #     mglearn.tools.heatmap(scores, xlabel='n_estimators', xticklabels=param_grid['n_estimators'],
    #                       ylabel='max_depth', yticklabels=param_grid['max_depth'], cmap="viridis", fmt='%0.1f')
    #     plt.show()

    # ランダムフォレストによる予測
    rfr = RandomForestRegressor(n_estimators=10,max_depth = 2, random_state=5)
    rfr.fit(x_train,y_train)
    x_test = np.linspace(8,50,1000).reshape(-1,1)
    predict = rfr.predict(x_test)

    # 現在のPerを計算に使用する
    per_value = get_per(per_url)
    now_value = np.array(per_value).reshape(-1,1)
    estimate = rfr.predict(now_value)

    # グラフ化
    plt.rcParams["legend.framealpha"] = 1
    plt.rcParams['figure.subplot.bottom'] = 0.15
    plt.rcParams['figure.subplot.top'] = 0.90
    plt.figure(figsize=(10,3.5))


    plt.scatter(df4['PE Ratio_x'],df4['afteryearsReturn'],s=100,alpha=0.2, label='Since 1980/01/01')
    plt.vlines([per_value],0.5,df4['afteryearsReturn'].max(),color='black', label='Current PE Ratio')
    plt.hlines([1],0,50,color='black',linestyles='dotted')
    plt.plot(x_test[:,0],predict,c='r',label='Predict by RandomForest')
    plt.text(now_value+1,df4['afteryearsReturn'].max()/2,'PER =' + str(per_value) +'\npredict ='+str(round(estimate[0],2)),fontsize=13)
    plt.xlim([0,50])
    plt.legend(fontsize=12)
    plt.title('{}年後のリターン予測'.format(afteryears),fontsize=18)
    plt.xlabel('PE ratio',fontsize=15)
    plt.ylabel('{}年後のリターン(倍)'.format(afteryears),fontsize=15)
    plt.xticks(fontsize=11)
    plt.yticks(fontsize=12)
    plt.grid()
    plt.savefig(str(BASE_DIR)+'/static/images/per_predict.png')
    # plt.show()
