# Generated by Django 3.0.5 on 2020-05-01 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Images',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img_name', models.CharField(blank=True, max_length=25)),
                ('img_description', models.TextField(blank=True, max_length=250)),
                ('img_format', models.CharField(max_length=5)),
                ('favourite', models.BooleanField()),
                ('uploaded_image', models.ImageField(upload_to='pics/')),
                ('width', models.IntegerField(default=0)),
                ('height', models.IntegerField(default=0)),
            ],
        ),
    ]
