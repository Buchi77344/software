# Generated by Django 5.0.1 on 2024-08-26 23:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0022_alter_user_school_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='userid',
            name='session_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
