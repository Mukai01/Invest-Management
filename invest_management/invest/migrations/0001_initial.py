# Generated by Django 3.2.7 on 2021-10-11 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SampleModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invest_date', models.DateTimeField()),
                ('topix_price', models.IntegerField()),
                ('topix_invest', models.IntegerField()),
            ],
        ),
    ]
