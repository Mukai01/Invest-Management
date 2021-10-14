# 以下でデータベースを作成する
# python3 manage.py makemigrations
# python3 manage.py migrate
from django.db import models

class Invest(models.Model): 
    invest_date = models.DateTimeField()
    topix_price = models.IntegerField(null = True)
    topix_invest = models.IntegerField(null = True)
    developed_price = models.IntegerField(null = True)
    developed_invest = models.IntegerField(null = True)
    developing_price = models.IntegerField(null = True)
    developing_invest = models.IntegerField(null = True)
    all_price = models.IntegerField(null = True)
    all_invest = models.IntegerField(null = True)