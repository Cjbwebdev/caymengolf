# Generated manually for bookings app
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TeeTime",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("time", models.TimeField()),
                ("is_available", models.BooleanField(default=True)),
                ("max_players", models.IntegerField(default=4)),
                ("booked_players", models.IntegerField(default=0)),
            ],
            options={
                "ordering": ["date", "time"],
                "unique_together": {("date", "time")},
            },
        ),
        migrations.CreateModel(
            name="LessonSlot",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("time", models.TimeField()),
                ("duration", models.IntegerField(default=45)),
                ("is_available", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["date", "time"],
                "unique_together": {("date", "time")},
            },
        ),
        migrations.CreateModel(
            name="Booking",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("num_players", models.IntegerField(default=1)),
                ("player_names", models.TextField(default="")),
                ("notes", models.TextField(blank=True, default="")),
                ("is_cancelled", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("tee_time", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="bookings.teetime")),
                ("lesson_slot", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="bookings.lessonslot")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="auth.user")),
            ],
        ),
    ]
