# Generated by Django 5.1.2 on 2024-11-02 12:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='member_id',
            new_name='user_id',
        ),
    ]
