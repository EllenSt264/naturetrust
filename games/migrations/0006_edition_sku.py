# Generated by Django 3.2.6 on 2021-09-20 16:20

from django.db import migrations, models
import games.models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0005_auto_20210824_2333'),
    ]

    operations = [
        migrations.AddField(
            model_name='edition',
            name='sku',
            field=models.CharField(default=games.models.generate_sku, editable=False, max_length=12, unique=True),
        ),
    ]
