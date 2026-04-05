# New models to add for the next batch of features

MODELS = """
# ═══════════════════════════════════════════
# COURSE CONDITIONS (Dan updates daily)
# ═══════════════════════════════════════════

class CourseCondition(models.Model):
    CONDITIONS = [
        ('dry', 'Dry / Fast Greens'),
        ('normal', 'Normal / Good Playing'),
        ('wet', 'Wet / Heavy Ground'),
        ('frozen', 'Frozen / Temporary Greens'),
        ('closed', 'Course Closed'),
    ]
    GREEN_SPEED = [
        ('slow', 'Slow (< 6)'),
        ('medium', 'Medium (6-8)'),
        ('fast', 'Fast (8+)'),
    ]
    
    date = models.DateField(unique=True)
    condition = models.CharField(max_length=20, choices=CONDITIONS, default='normal')
    green_speed = models.CharField(max_length=10, choices=GREEN_SPEED, blank=True, default='')
    notes = models.TextField(blank=True, default="")
    updated_by = models.CharField(max_length=100, default="admin")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.date} — {self.get_condition_display()}'


# ═══════════════════════════════════════════
# FOOD & BEVERAGE PRE-ORDER
# ═══════════════════════════════════════════

class FoodItem(models.Model):
    CATEGORY_CHOICES = [
        ('food', 'Hot Food'),
        ('cold', 'Cold Snacks'),
        ('drinks', 'Drinks'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_available = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['category', 'sort_order']

    def __str__(self):
        return f'{self.name} — £{self.price}'


class FoodOrder(models.Model):
    booking = models.ForeignKey("bookings.Booking", on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    order_date = models.DateField()
    tee_time = models.CharField(max_length=50, blank=True, default="")
    items = models.JSONField(default=dict)  # {"item_id": qty, ...}
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    notes = models.TextField(blank=True, default="")
    collection_time = models.CharField(max_length=20, default="After round")
    is_paid = models.BooleanField(default=False)
    stripe_session_id = models.CharField(max_length=300, blank=True, default="")
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('ready', 'Ready for Collection'),
        ('collected', 'Collected'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Food order for {self.user.username} on {self.order_date}'


# ═══════════════════════════════════════════
# GIFT VOUCHERS
# ═══════════════════════════════════════════

class GiftVoucher(models.Model):
    VOUCHER_TYPE = [
        ('tee_time', 'Tee Time Voucher'),
        ('lesson', 'Lesson Voucher'),
        ('food', '19th Hole Food Voucher'),
        ('custom', 'Custom Amount'),
    ]
    
    code = models.CharField(max_length=20, unique=True, db_index=True)
    voucher_type = models.CharField(max_length=20, choices=VOUCHER_TYPE)
    value = models.DecimalField(max_digits=8, decimal_places=2)
    purchaser_email = models.EmailField()
    recipient_email = models.EmailField(blank=True, default="")
    recipient_name = models.CharField(max_length=200, blank=True, default="")
    personal_message = models.TextField(blank=True, default="")
    is_redeemed = models.BooleanField(default=False)
    purchased_at = models.DateTimeField(auto_now_add=True)
    redeemed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-purchased_at']

    def __str__(self):
        return f'Voucher {self.code} — £{self.value}'
"""

# Write the migration file with these models
print("Models defined above — add them to golfers/models.py or create booking/menus/models.py")
print("Ready to implement!")
