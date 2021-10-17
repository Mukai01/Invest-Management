# ライブラリインポート
from urllib import request
from bs4 import BeautifulSoup
import re
import matplotlib.pyplot as plt
import japanize_matplotlib
def get_stockvalue(url):
    # htmlを取得
    response = request.urlopen(url)
    content = response.read()
    response.close()
    html = content.decode()
    #print(html)
    
    # 以下の要素を取りに行く
    # <td class="br0"><span class="value-01">15,360</span> 円 （10/1）</td>
    soup = BeautifulSoup(html)
    table_elements = soup.find_all('td', class_='br0')
    
    # 数値のみに変換
    stock_value = table_elements[0].get_text()
    p = re.compile(r'\d+,\d+')
    stock_value = p.match(stock_value).group()
    stock_value = int(stock_value.replace(',',''))
    return stock_value

def calculate_algorithm():
    # urlを定義
    url_dic = {
        'developed':'https://www.rakuten-sec.co.jp/web/fund/detail/?ID=JP90C0009VE0',
        'japan':'https://www.rakuten-sec.co.jp/web/fund/detail/?ID=JP90C000ENA9',
        'developing':'https://www.rakuten-sec.co.jp/web/fund/detail/?ID=JP90C000F7H5',
        'all country':'https://www.rakuten-sec.co.jp/web/fund/detail/?ID=JP90C000H1T1',
    }
    # Target Portfolio
    portfolio_dic = {
        'developed':0.31875,
        'japan':0.16875,
        'developing':0.0125,
        'all country':0.5,
    }
    
    # 株の基準額
    stock_base_dic = {
        'developed':24159,
        'japan':14917,
        'developing':12748,
        'all country':15698
    }

    # 名前リスト
    name_list =["先進国", "日本", "新興国", "全世界"]
    # 毎週の基準投資額
    invest_per_week = 137416.6
    
    # 実行
    stock_dic = {}
    for i in url_dic:
        stock_value = get_stockvalue(url_dic[i])
        stock_dic[i] = stock_value
        print('{}の基準価額は{}でした...'.format(i, stock_dic[i]))
        
    # 購入額を計算    
    invest_algorithm_dic = {}
    invest_base_dic = {}
    for i in stock_dic:
        # 補正係数を計算
        correction = 2**((1-stock_dic[i]/stock_base_dic[i])*10) 
        # 補正係数をかける
        invest_algorithm_dic[i] = invest_per_week * portfolio_dic[i] * correction
        # 基準投資額も計算
        invest_base_dic[i] =  invest_per_week * portfolio_dic[i]

    # 結果を格納
    print("基準価額:", stock_dic)
    print("基準投資額:", invest_base_dic)
    print("計算購入額:", invest_algorithm_dic)
    return stock_dic, invest_base_dic, invest_algorithm_dic

def calculate_only(developed_price, topix_price, developing_price, all_price):
    # Target Portfolio
    portfolio_dic = {
        'developed':0.31875,
        'japan':0.16875,
        'developing':0.0125,
        'all country':0.5,
    }
    
    # 株の基準額
    stock_base_dic = {
        'developed':24159,
        'japan':14917,
        'developing':12748,
        'all country':15698
    }

    # 名前リスト
    name_list =["先進国", "日本", "新興国", "全世界"]
    # 毎週の基準投資額
    invest_per_week = 137416.6
    
    # 実行
    stock_dic = {
        'developed':int(developed_price),
        'japan':int(topix_price),
        'developing':int(developing_price),
        'all country':int(all_price)
    }
        
    # 購入額を計算    
    invest_algorithm_dic = {}
    invest_base_dic = {}
    for i in stock_dic:
        # 補正係数を計算
        correction = 2**((1-stock_dic[i]/stock_base_dic[i])*10) 
        # 補正係数をかける
        invest_algorithm_dic[i] = invest_per_week * portfolio_dic[i] * correction
        # 基準投資額も計算
        invest_base_dic[i] =  invest_per_week * portfolio_dic[i]

    # 結果を格納
    print("基準価額:", stock_dic)
    print("基準投資額:", invest_base_dic)
    print("計算購入額:", invest_algorithm_dic)
    return stock_dic, invest_base_dic, invest_algorithm_dic
