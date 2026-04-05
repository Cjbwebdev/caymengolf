# Generated manually for billing app
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Invoice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("invoice_type", models.CharField(choices=[("tee_time", "Tee Time Booking"), ("lesson", "Lesson Booking")], max_length=20)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("paid", "Paid"), ("failed", "Failed"), ("refunded", "Refunded")], default="pending", max_length=20)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=8)),
                ("description", models.CharField(default="", max_length=300)),
                ("stripe_session_id", models.CharField(blank=True, default="", max_length=300)),
                ("stripe_payment_intent", models.CharField(blank=True, default="", max_length=300)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("user", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="auth.user")),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
