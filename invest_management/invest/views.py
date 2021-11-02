from django.shortcuts import render, redirect
from django.utils import timezone
from django_pandas.io import read_frame
from .models import Invest
from .forms import ExpenditureForm
from urllib import request
from bs4 import BeautifulSoup
import re
import pytz
import datetime
import calendar
from .analysis_code import purchase_algorithm, invest_timeseries, per_predict, random_predict, asset_visualization, portfolio_calculate, flow_visualization
import time
import pandas as pd
import numpy as np

# 表示の設定
axis_visible = True
correction = 1.0

def tradeview(request):
    # 現在日時を取得
    today = str(timezone.now()+ datetime.timedelta(hours=9)).split('-')
    today_date = today[0]+'/'+today[1]+'/'+today[2][:2]

    # modelのInvestを逆順に読み込み
    invest = Invest.objects.order_by('invest_date' ).reverse()

    # 投資の時系列グラフ化
    df = read_frame(invest, fieldnames=['invest_date', 'topix_price', 'topix_invest', 'developed_price', 'developed_invest', 
        'developing_price', 'developing_invest', 'all_price', 'all_invest'])
    invest_timeseries.make_invest_timeseries(df)

    # totalを計算
    total_topix = 0
    total_developed = 0
    total_developing = 0
    total_all = 0
    for i in invest:
        date = str(i.invest_date).split(' ')[0] # dateの書式を変換
        i.invest_date = '/'.join(date.split('-')[1:3])
        total_topix += i.topix_invest
        total_developed += i.developed_invest
        total_developing += i.developing_invest
        total_all += i.all_invest

    # Formに表示する初期値を設定
    initial_dict = dict(invest_date=today_date, topix_price=0, topix_invest=0,
        developed_price=0, developed_invest=0, developing_price=0, developing_invest=0,
        all_price=0, all_invest=0)

    # 初期値をformに引き継ぎ
    form = ExpenditureForm(initial=initial_dict)

    # contextを作成
    context = {
        'year' : today[0],
        'month' : today[1],
        'day' : today[2][:2],
        'invest' : invest,
        'form' : form,
        'total_topix' : total_topix,
        'total_developed' : total_developed,
        'total_developing' : total_developing,
        'total_all' : total_all,
    }

    # フォームからデータが送られてきた場合はここ
    if request.method == 'POST': 
        # calculateボタンが押された場合
        if "calculate" in request.POST:
            
            # アルゴリズムを動作
            stock_dic, invest_base_dic, invest_algorithm_dic = purchase_algorithm.calculate_algorithm()

            # 初期値に設定
            initial_dict = dict(invest_date=today_date, topix_price=stock_dic['japan'], topix_invest=round(invest_algorithm_dic['japan']/2),
                developed_price=stock_dic['developed'], developed_invest=round(invest_algorithm_dic['developed']/2),
                developing_price=stock_dic['developing'], developing_invest=round(invest_algorithm_dic['developing']/2),
                all_price=stock_dic['all country'], all_invest=round(invest_algorithm_dic['all country']/2))
            form = ExpenditureForm(request.GET or None, initial=initial_dict)

            # contextを作り直す
            context = {
                'year' : today[0],
                'month' : today[1],
                'day' : today[2][:2],
                'invest' : invest,
                'form' : form,
                'total_topix' : total_topix,
                'total_developed' : total_developed,
                'total_developing' : total_developing,
                'total_all' : total_all,
            }
            
            # renderでページを表示
            return render(request, 'index.html', context)

        elif "re-calculate" in request.POST:
            print('再計算します...')
            data = request.POST
            # form情報を取得
            topix_price = data['topix_price']
            developed_price = data['developed_price']
            developing_price = data['developing_price']
            all_price = data['all_price']
            
            stock_dic, invest_base_dic, invest_algorithm_dic = purchase_algorithm.calculate_only(developed_price, topix_price, developing_price, all_price)
            
            # 初期値に設定
            initial_dict = dict(invest_date=today_date, topix_price=stock_dic['japan'], topix_invest=round(invest_algorithm_dic['japan']/2),
                developed_price=stock_dic['developed'], developed_invest=round(invest_algorithm_dic['developed']/2),
                developing_price=stock_dic['developing'], developing_invest=round(invest_algorithm_dic['developing']/2),
                all_price=stock_dic['all country'], all_invest=round(invest_algorithm_dic['all country']/2))
            form = ExpenditureForm(request.GET or None, initial=initial_dict)

            # contextを作り直す
            context = {
                'year' : today[0],
                'month' : today[1],
                'day' : today[2][:2],
                'invest' : invest,
                'form' : form,
                'total_topix' : total_topix,
                'total_developed' : total_developed,
                'total_developing' : total_developing,
                'total_all' : total_all,
            }
            
            # renderでページを表示
            return render(request, 'index.html', context)

        
        # 抽出ボタンが押されたとき
        elif "extract" in request.POST:
            data = request.POST
            # データを抽出
            invest = Invest.objects.filter(invest_date__month = data['extract'][4:], invest_date__year = data['extract'][:4]).order_by('invest_date').reverse()

            # 時系列をグラフ化
            df = read_frame(invest, fieldnames=['invest_date', 'topix_price', 'topix_invest', 'developed_price', 'developed_invest', 
                'developing_price', 'developing_invest', 'all_price', 'all_invest'])
            invest_timeseries.make_invest_timeseries(df)

            # dateの書式を変換、totalを計算
            total_topix = 0
            total_developed = 0
            total_developing = 0
            total_all = 0
            for i in invest:
                date = str(i.invest_date).split(' ')[0]
                i.invest_date = '/'.join(date.split('-')[1:3])
                total_topix += i.topix_invest
                total_developed += i.developed_invest
                total_developing += i.developing_invest
                total_all += i.all_invest

            # contextを作り直す
            context = {
                'year' : today[0],
                'month' : today[1],
                'day' : today[2][:2],
                'invest' : invest,
                'form' : form,
                'total_topix' : total_topix,
                'total_developed' : total_developed,
                'total_developing' : total_developing,
                'total_all' : total_all,
                'extract_input' : data['extract']
            }

            return render(request, 'index.html', context)

        # 登録ボタンが押された場合
        elif "add" in request.POST:
            # データを取得
            data = request.POST
    
            # form情報を取得
            invest_date = data['invest_date']
            topix_price = data['topix_price']
            topix_invest = data['topix_invest']
            developed_price = data['developed_price']
            developed_invest = data['developed_invest']
            developing_price = data['developing_price']
            developing_invest = data['developing_invest']
            all_price = data['all_price']
            all_invest = data['all_invest']

            # 書式、タイムゾーンの変更
            invest_date = timezone.datetime.strptime(invest_date, "%Y/%m/%d")
            tokyo_timezone = pytz.timezone('Asia/Tokyo') 
            invest_date = tokyo_timezone.localize(invest_date)
            invest_date += datetime.timedelta(hours=9)    #時間を9時間遅らせる
            
            # データベースにデータを格納
            Invest.objects.create(    
                    invest_date = invest_date,
                    topix_price = topix_price,
                    topix_invest = topix_invest,
                    developed_price = developed_price,
                    developed_invest = developed_invest,
                    developing_price = developing_price,
                    developing_invest = developing_invest,
                    all_price = all_price,
                    all_invest = all_invest,
                    )

            return redirect(to = '/trade')
    # 何もボタンが押されていない場合
    return render(request, 'index.html', context)

def analysisview(request):    
    # 現在日時を取得
    today = str(timezone.now()+ datetime.timedelta(hours=9)).split('-')
    today_date = today[0]+'/'+today[1]+'/'+today[2][:2]

    # 年数が入力されたとき
    if "predict_year" in request.POST:
        data = request.POST
        afteryears = int(data['predict_year'])
        # perのグラフを作成
        per_predict.random_forest_predict_byshillerper(afteryears)
        per_predict.random_forest_predict_byper(afteryears)

    # デフォルトを5に設定
    else:
        afteryears=5
    
    # シミュレーション情報が入力されたとき
    if "sim_num" in request.POST and "sim_year" in request.POST:
        data = request.POST
        sim_num = int(data['sim_num'])
        sim_year = int(data['sim_year'])
        random_predict.randomwalk_simulate(sim_num,sim_year)
    # デフォルトの値を設定
    else:
        sim_num = 100
        sim_year = 5

    # グラフは不要なのでFalseに設定
    make_graph = False
    developed_rate, japan_rate, developing_rate = asset_visualization.visualization(axis_visible, make_graph)
    # 値を四捨五入
    developed_rate, japan_rate, developing_rate = round(developed_rate,2), round(japan_rate,2), round(developing_rate,2)

    # 効率的フロンティアグラフの計算ボタンが押された場合
    if "portfolio_1" in request.POST and "portfolio_2" in request.POST and "portfolio_3" in request.POST:
        data = request.POST
        developed_rate = float(data['portfolio_1'])
        japan_rate = float(data['portfolio_2'])
        developing_rate = float(data['portfolio_3'])
        # x_nowを設定する
        x_now=[0,0,0,0,0]
        x_now[1] = japan_rate
        x_now[3] = developed_rate
        x_now[4] = developing_rate
        # 計算プログラムを呼び出す
        portfolio_calculate.portfolio_cal(x_now)

    # contextを作成
    context = {
        'year' : today[0],
        'month' : today[1],
        'day' : today[2][:2],
        'afteryears' : afteryears,
        'sim_num' : sim_num,
        'sim_year' : sim_year,
        'developed_rate' : developed_rate,
        'japan_rate' : japan_rate,
        'developing_rate' : developing_rate,
    }

    return render(request, 'analysis.html', context)

def assetview(request):
    # 更新ボタンが押されたときだけグラフを作成
    if "update" in request.POST:
        # 入力結果の処理
        data = request.POST
        # グラフ作成
        make_graph = True
        asset_visualization.visualization(axis_visible, make_graph)

    # 現在日時を取得
    today = str(timezone.now()+ datetime.timedelta(hours=9)).split('-')
    today_date = today[0]+'/'+today[1]+'/'+today[2][:2]

    # contextを作成
    context = {
        'year' : today[0],
        'month' : today[1],
        'day' : today[2][:2],
    }

    return render(request, 'asset.html', context)


def flowview(request):
    # 現在日時を取得
    today = str(timezone.now()+ datetime.timedelta(hours=9)).split('-')
    today_date = today[0]+'/'+today[1]+'/'+today[2][:2]

    # contextを作成
    context = {
        'year' : today[0],
        'month' : today[1],
        'day' : today[2][:2],
    }

    if "extract_month" in request.POST:
        # 入力結果の処理
        data = request.POST
        month_input = data['extract_month']
        extract_month = month_input
        
        try:
            # 入力結果が6文字の場合
            if len(extract_month)==6:
                extract_month = pd.to_datetime(extract_month, format="%Y%m")
            # 入力結果が8文字の場合
            else:
                extract_month = pd.to_datetime(extract_month, format="%Y%m%d")

            # contextを更新
            context = {
                'year' : today[0],
                'month' : today[1],
                'day' : today[2][:2],
                'extract_month' : month_input
            }

        # それ以外の場合はNoneとする
        except ValueError:
            extract_month = None

        # flow_visual関数の呼び出し
        flow_visualization.flow_visual(extract_month, axis_visible, correction)
    
    # renderでflow.htmlを表示
    return render(request, 'flow.html', context)