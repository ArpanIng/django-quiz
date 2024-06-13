# Generated by Django 4.2.13 on 2024-06-13 03:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='question_type',
            field=models.CharField(choices=[('MC', 'Multiple Choice'), ('MSMC', 'Multi select Multiple Choice')], default='MC', max_length=4),
        ),
        migrations.AddField(
            model_name='quiz',
            name='popularity',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='result',
            name='submitted_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddIndex(
            model_name='quiz',
            index=models.Index(fields=['popularity'], name='quiz_quiz_popular_c4ca12_idx'),
        ),
    ]