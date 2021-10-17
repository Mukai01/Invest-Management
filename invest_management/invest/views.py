from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Invest
from .forms import ExpenditureForm
from urllib import request
from bs4 import BeautifulSoup
import re
import pytz
import datetime
import calendar
from .analysis_code import purchase_algorithm, invest_timeseries

# urls.pyから呼び出される
def index(request):
    # 現在日時を取得
    today = str(timezone.now()+ datetime.timedelta(hours=9)).split('-')
    today_date = today[0]+'/'+today[1]+'/'+today[2][:2]

    # modelのInvestを読み込み
    invest = Invest.objects.order_by('invest_date' ).reverse()


    # 投資の時系列グラフ化
    from django_pandas.io import read_frame
    import pandas as pd
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
        
        # 抽出ボタンが押されたとき
        elif "extract" in request.POST:
            data = request.POST
            # データを抽出
            invest = Invest.objects.filter(invest_date__month = data['extract'][4:], invest_date__year = data['extract'][:4]).order_by('invest_date').reverse()

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

            return redirect(to = '/invest')
    # 何もボタンが押されていない場合
    return render(request, 'index.html', context)