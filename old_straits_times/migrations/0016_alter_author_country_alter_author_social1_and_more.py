# Generated by Django 4.1.6 on 2023-02-22 03:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('old_straits_times', '0015_alter_author_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='country',
            field=models.CharField(blank=True, default='', max_length=60, null=True),
        ),
        migrations.AlterField(
            model_name='author',
            name='social1',
            field=models.CharField(blank=True, default='', max_length=120, null=True),
        ),
        migrations.AlterField(
            model_name='author',
            name='social2',
            field=models.CharField(blank=True, default='', max_length=120, null=True),
        ),
        migrations.AlterField(
            model_name='author',
            name='social3',
            field=models.CharField(blank=True, default='', max_length=120, null=True),
        ),
        migrations.AlterField(
            model_name='author',
            name='social4',
            field=models.CharField(blank=True, default='', max_length=120, null=True),
        ),
    ]
