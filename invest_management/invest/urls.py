from django.contrib import admin
from django.urls import path
from .views import tradeview, analysisview, assetview, flowview

urlpatterns = [
    path('trade/', tradeview, name='trade'),
    path('analysis/', analysisview, name='analysis'),
    path('asset/', assetview, name='asset'),
    path('flow/', flowview, name='flow'),
]