# Generated manually for lessons app
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name="LessonType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField()),
                ("duration_minutes", models.IntegerField(default=60)),
                ("price", models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["price"],
            },
        ),
    ]
