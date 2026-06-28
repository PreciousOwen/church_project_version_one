from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0009_member_step6_additions"),
    ]

    operations = [
        migrations.AddField(
            model_name="memberapplication",
            name="membership_number",
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
