# Generated by Django 5.0.1 on 2024-08-26 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0021_name_school'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='school_name',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
