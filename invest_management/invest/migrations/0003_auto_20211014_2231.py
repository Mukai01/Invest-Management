# Generated by Django 3.2.7 on 2021-10-14 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invest', '0002_rename_samplemodel_invest'),
    ]

    operations = [
        migrations.AddField(
            model_name='invest',
            name='all_invest',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='invest',
            name='all_price',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='invest',
            name='developed_invest',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='invest',
            name='developed_price',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='invest',
            name='developing_invest',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='invest',
            name='developing_price',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='invest',
            name='topix_invest',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='invest',
            name='topix_price',
            field=models.IntegerField(null=True),
        ),
    ]
