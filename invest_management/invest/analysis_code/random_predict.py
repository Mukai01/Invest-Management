#データ読み込み
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib
from scipy.stats import norm
import seaborn as sns
from scipy.stats import t
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM
from tqdm import tqdm
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent

#関数を定義
def make_return(loc1, loc2, scale1, scale2):
#     loc1 = 1.0005478168389164
#     loc2 = 0.9971137713072488
#     scale1 = 0.01024285501985374
#     scale2 = 0.029152921438795287
    
    #5%の確率で異常状態の正規分布からサンプリング
    if np.random.rand()<0.05:
        a=np.random.normal(loc2,scale2)
        svm_result=-1
    #95%の確率で正常状態の正規分布からサンプリング
    else:
        a=np.random.normal(loc1,scale1)
        svm_result=1
    return a,svm_result

def randomwalk_simulate(sim_num, years):
    # ファイル読み込み
    file='C:/Users/nakam/Dropbox/資産/Django/data/FTOPIX.xlsx'
    df=pd.read_excel(file)

    #出来高は不要なので削除
    del df['出来高']

    #前日の変数を追加
    for i in ['始値', '高値', '安値', '終値']:
        df[i+"(前日)"]=df[i].shift(1)
    df['前日比率']=df['終値']/df['終値(前日)']

    # ボラティリティの計算
    df['当日の高値-当日の安値']=df['高値']-df['安値']
    df['当日の高値-前日の終値']=df['高値']-df['終値(前日)']
    df['前日の終値-当日の安値']=df['終値(前日)']-df['安値']
    df['True Range']=df[['当日の高値-当日の安値','当日の高値-前日の終値','前日の終値-当日の安値']].max(axis=1)
    df['Typical Price']=(df['高値']+df['安値']+df['終値'])/3
    df['ボラティリティ']=df['True Range']/df['Typical Price']

    df=df.dropna()
    df=df[['日付', '終値', '前日比率', 'ボラティリティ']]
    # display(df)

    #正規化を実施
    X_train=df[['前日比率','ボラティリティ']]

    sc = StandardScaler()
    X_train_std = sc.fit_transform(X_train)
    X_train_std

    #one class svmでデータを正常・異常に分ける
    clf = OneClassSVM(nu=0.05, kernel='rbf', gamma=0.5)
    clf.fit(X_train_std)
    pred = clf.predict(X_train_std)

    X_train['svm']=pred

    #正規分布を推定
    df_temp = X_train[X_train['svm']==1]
    loc, scale = norm.fit(df_temp['前日比率'].dropna())
    df_temp_1=X_train[X_train['svm']==-1]
    loc1, scale1 = norm.fit(df_temp_1['前日比率'].dropna())

    #結果の箱を作成
    df_sim1=pd.DataFrame()

    #1000回シミュレーションを実行
    for j in tqdm(range(sim_num)):
        return_list=[]

        #1年間を240日と考えて、20年後までをシミュレーションする
        for i in range(240*years):
            a,svm_result=make_return(loc, loc1, scale, scale1)
            return_list.append(a)
        return_list=np.array(return_list)
        df_sim1[j]=return_list

    #累積リターンを計算
    df_sim2=df_sim1.cumprod()
    # display(df_sim2)

    #結果を可視化
    plt.rcParams["legend.framealpha"] = 1
    plt.rcParams['figure.subplot.bottom'] = 0.15
    plt.rcParams['figure.subplot.top'] = 0.90
    plt.figure(figsize=(10,3.5))

    num=0
    for i in df_sim2.columns:
        temp=df_sim2[i].iloc[:240*years]
        if temp.iloc[-1]<1:
            plt.plot(temp.index/240,temp,alpha=0.2,c='r')
            num=num+1
        else:
            plt.plot(temp.index/240,temp,alpha=0.2,c='g')

    plt.text(0, df_sim2.max().max()*0.7, "損失が出る確率：{}/{} \n95%点:{:.3f}倍 \n中央値:{:.3f}倍 \n5%点:{:.3f}倍".format(num,
        sim_num,df_sim2.iloc[240*years-1].quantile(0.95),df_sim2.iloc[240*years-1].median(),df_sim2.iloc[240*years-1].quantile(0.05)),fontsize=12)
    plt.title('{}年後のリターン予測({}回計算)'.format(years,sim_num),fontsize=18)
    plt.xlabel('(年)',fontsize=15)
    plt.ylabel('{}年後のリターン(倍)'.format(years),fontsize=15)
    plt.xticks(fontsize=11)
    plt.yticks(fontsize=12)
    plt.grid()

    plt.savefig(str(BASE_DIR)+'/static/images/random_predict.png')
    # plt.show()
    return df_sim2