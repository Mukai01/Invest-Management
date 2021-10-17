from django.contrib import admin
from .models import Invest

# csvインポートを実行するためにインポート
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.formats import base_formats

# admin.site.register(Invest)

class GuestResource(resources.ModelResource):
    class Meta:
        model = Invest
        fields = ('id','invest_date', 'topix_price', 'topix_invest', 'developed_price','developed_invest',
        'developing_price', 'developing_invest', 'all_price', 'all_invest')
        import_id_fields = ['id']


class GuestAdmin(ImportExportModelAdmin):
    list_display = (
        'invest_date', 'topix_price', 'topix_invest', 'developed_price','developed_invest',
        'developing_price', 'developing_invest', 'all_price', 'all_invest')

    resource_class = GuestResource
    formats = [base_formats.CSV]


admin.site.register(Invest, GuestAdmin)