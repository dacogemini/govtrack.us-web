# Generated by Django 2.0.8 on 2018-11-24 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0002_auto_20180811_1342'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='majority_party_percent_plus',
            field=models.FloatField(blank=True, help_text="The percent of positive votes among the majority party only. Null for votes that aren't yes/no (like election of the speaker, quorum calls).", null=True),
        ),
        migrations.AddField(
            model_name='vote',
            name='passed',
            field=models.NullBooleanField(help_text='Whether the vote passed or failed, for votes that have such an option. Otherwise None.'),
        ),
        migrations.AddField(
            model_name='voteoption',
            name='winner',
            field=models.NullBooleanField(help_text="If known, whether this Option is the one that was the vote's winner."),
        ),
    ]