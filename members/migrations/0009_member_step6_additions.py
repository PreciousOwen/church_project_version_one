from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0008_memberapplication_step6_additions"),
    ]

    operations = [
        migrations.AddField(
            model_name="member",
            name="has_membership_number",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="member",
            name="membership_registration_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="member",
            name="membership_registered_full_name",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="member",
            name="pledge_building",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name="member",
            name="pledge_other",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name="member",
            name="pledge_stewardship",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name="member",
            name="pledge_year",
            field=models.IntegerField(default=0),
        ),
    ]
