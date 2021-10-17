from django.contrib import admin
from django.urls import path
from .views import tradeview, analysisview

urlpatterns = [
    path('trade/', tradeview, name='trade'),
    path('analysis/', analysisview, name='analysis'),
]