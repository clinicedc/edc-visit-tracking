# Generated by Django 3.1.8 on 2021-04-23 11:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("edc_visit_tracking", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="subjectvisitmissedreasons",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="visitreasons",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
