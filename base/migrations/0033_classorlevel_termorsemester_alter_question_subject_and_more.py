# Generated by Django 5.0.1 on 2024-08-30 09:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0032_loding_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassOrLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('jss1', 'JSS 1'), ('jss2', 'JSS 2'), ('jss3', 'JSS 3'), ('sss1', 'SSS 1'), ('sss2', 'SSS 2'), ('sss3', 'SSS 3'), ('cbt', 'CBT'), ('level_100', 'Level 100'), ('level_200', 'Level 200'), ('level_300', 'Level 300'), ('level_400', 'Level 400')], max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='TermOrSemester',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('first_term', 'First Term'), ('second_term', 'Second Term'), ('third_term', 'Third Term'), ('first_semester', 'First Semester'), ('second_semester', 'Second Semester')], max_length=20)),
            ],
        ),
        migrations.AlterField(
            model_name='question',
            name='subject',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.subject'),
        ),
        migrations.AddField(
            model_name='question',
            name='class_or_level',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.classorlevel'),
        ),
        migrations.AddField(
            model_name='question',
            name='term_or_semester',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.termorsemester'),
        ),
    ]
