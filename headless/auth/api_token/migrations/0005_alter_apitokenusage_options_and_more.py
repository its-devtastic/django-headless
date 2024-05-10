# Generated by Django 5.1 on 2024-09-16 11:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("headless_api_token", "0004_alter_apitoken_description_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="apitokenusage",
            options={
                "ordering": ["-timestamp"],
                "verbose_name": "API Token Usage",
                "verbose_name_plural": "API Token Usage",
            },
        ),
        migrations.AddField(
            model_name="apitokenusage",
            name="query_params",
            field=models.CharField(
                default="",
                editable=False,
                max_length=255,
                verbose_name="Query parameters",
            ),
        ),
        migrations.AlterField(
            model_name="apitokenusage",
            name="method",
            field=models.CharField(
                editable=False, max_length=10, verbose_name="Method"
            ),
        ),
        migrations.AlterField(
            model_name="apitokenusage",
            name="path",
            field=models.CharField(editable=False, max_length=255, verbose_name="Path"),
        ),
        migrations.AlterField(
            model_name="apitokenusage",
            name="token",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="usages",
                to="headless_api_token.apitoken",
                verbose_name="Token",
            ),
        ),
    ]
