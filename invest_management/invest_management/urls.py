from django.contrib import admin
from django.urls import path, include

# admin以外の時はinvest.urlsを呼び出す
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('invest.urls')),
]
