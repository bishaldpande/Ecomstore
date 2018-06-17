# Generated by Django 2.0.5 on 2018-06-12 08:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_category_product'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('district', models.CharField(max_length=250)),
                ('city', models.CharField(max_length=250)),
                ('wardno', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.Address'),
        ),
    ]
