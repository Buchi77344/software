# Generated by Django 5.0.1 on 2024-08-29 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0030_result_login'),
    ]

    operations = [
        migrations.CreateModel(
            name='Loding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login', models.BooleanField(default=False)),
            ],
        ),
        migrations.RemoveField(
            model_name='result',
            name='login',
        ),
    ]
