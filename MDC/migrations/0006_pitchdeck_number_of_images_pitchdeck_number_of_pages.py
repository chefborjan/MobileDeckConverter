# Generated by Django 4.2.1 on 2023-05-27 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MDC', '0005_alter_deckimage_image_alter_pitchdeck_original_deck'),
    ]

    operations = [
        migrations.AddField(
            model_name='pitchdeck',
            name='number_of_images',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pitchdeck',
            name='number_of_pages',
            field=models.IntegerField(default=0),
        ),
    ]
