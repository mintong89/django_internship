# Generated by Django 4.1.6 on 2023-02-15 03:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('old_straits_times', '0003_rename_last_update_date_story_date_last_updated_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='story',
            name='date_published',
            field=models.DateTimeField(auto_now_add=True, verbose_name='date published'),
        ),
    ]
