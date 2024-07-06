# Generated by Django 3.2.3 on 2023-04-28 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0012_image_postimage_post_images'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, upload_to='posts/', verbose_name='Картинка (можно добавить только одну)'),
        ),
        migrations.AlterField(
            model_name='post',
            name='images',
            field=models.ManyToManyField(through='posts.PostImage', to='posts.Image', verbose_name='Картинки'),
        ),
    ]