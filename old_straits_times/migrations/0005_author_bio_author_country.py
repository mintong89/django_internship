# Generated by Django 4.1.6 on 2023-02-16 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('old_straits_times', '0004_alter_story_date_published'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='bio',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='author',
            name='country',
            field=models.CharField(default='', max_length=60),
        ),
    ]
