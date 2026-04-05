# Generated manually for golfers app
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="GolferProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("display_name", models.CharField(blank=True, max_length=100)),
                ("phone", models.CharField(blank=True, max_length=20)),
                ("handicap_index", models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True)),
                ("home_course", models.CharField(default="Cayman Golf, Brixham", max_length=200)),
                ("is_public", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="golf_profile", to="auth.user")),
            ],
        ),
        migrations.CreateModel(
            name="Score",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("total_score", models.IntegerField()),
                ("par", models.IntegerField(default=71)),
                ("front_9", models.IntegerField(blank=True, null=True)),
                ("back_9", models.IntegerField(blank=True, null=True)),
                ("hole_scores", models.JSONField(blank=True, default=dict, help_text="Dict of hole_number: score (1-18)")),
                ("handicap_at_time", models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True)),
                ("league", models.CharField(choices=[("all", "All"), ("junior", "Junior (Under 18)"), ("senior", "Senior (55+)"), ("female", "Female")], default="all", max_length=10)),
                ("course_conditions", models.CharField(blank=True, default="", max_length=30)),
                ("notes", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("golfer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="scores", to="golfers.golferprofile")),
            ],
            options={
                "ordering": ["-date"],
            },
        ),
        migrations.CreateModel(
            name="WeeklyLeaderboard",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("score", models.IntegerField()),
                ("week_start", models.DateField()),
                ("week_end", models.DateField()),
                ("golfer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="golfers.golferprofile")),
            ],
            options={
                "ordering": ["score"],
                "unique_together": {("golfer", "week_start")},
            },
        ),
    ]
