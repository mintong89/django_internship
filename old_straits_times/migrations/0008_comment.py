# Generated by Django 4.1.6 on 2023-02-20 07:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('old_straits_times', '0007_author_social1_author_social2_author_social3_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(blank=True)),
                ('date_published', models.DateTimeField(auto_now_add=True, verbose_name='date published')),
                ('edited', models.BooleanField(default=False)),
                ('commenter', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('dislikes', models.ManyToManyField(related_name='dislikeses', to=settings.AUTH_USER_MODEL)),
                ('likes', models.ManyToManyField(related_name='likeses', to=settings.AUTH_USER_MODEL)),
                ('reply_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='old_straits_times.comment')),
                ('story', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='old_straits_times.story')),
            ],
        ),
    ]
