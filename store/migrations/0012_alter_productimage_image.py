# Generated by Django 4.1.3 on 2022-11-21 12:59

from django.db import migrations, models
import store.validators


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_alter_orderitem_order_productimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=models.ImageField(upload_to='store/images', validators=[store.validators.validate_file_size]),
        ),
    ]
