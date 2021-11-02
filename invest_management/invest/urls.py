from django.contrib import admin
from django.urls import path
# viewをimport
from .views import tradeview, analysisview, assetview, flowview

# urlに一致したときにviewを呼び出す
urlpatterns = [
    path('trade/', tradeview, name='trade'),
    path('analysis/', analysisview, name='analysis'),
    path('asset/', assetview, name='asset'),
    path('flow/', flowview, name='flow'),
]