# Generated by Django 5.0.1 on 2024-08-27 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0027_remove_examsession_session_id_userexamsessionx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='examsession',
            name='submit',
            field=models.BooleanField(default=False),
        ),
    ]
