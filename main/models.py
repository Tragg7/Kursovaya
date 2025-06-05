from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

import shutil
import os
# --- Пользователь ---
class User(AbstractUser):
    is_courier = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

# --- Блюда ---
class Product(models.Model):
    CATEGORY_CHOICES = [
        ("Горячее", "Горячее"),
        ("Второе", "Второе"),
        ("Напитки", "Напитки"),
        ("Десерты", "Десерты"),
    ]

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to="uploads/")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.name

# --- Заказ ---
class Order(models.Model):
    STATUS_CHOICES = [
        ("Курьер забрал заказ и направляется к вам", "Курьер забрал заказ и направляется к вам"),
        ("Заказ доставлен", "Заказ доставлен"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default="Курьер забрал заказ и направляется к вам")
    courier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="deliveries")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Заказ #{self.pk} от {self.user.username}"

# --- Позиции заказа ---
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def total_price(self):
        return self.quantity * self.product.price

@receiver(post_save, sender=Product)
def copy_product_image_to_static(sender, instance, **kwargs):
    if instance.image:
        source_path = instance.image.path  # media/uploads/...
        filename = os.path.basename(source_path)
        destination_dir = os.path.join('main', 'static', 'uploads')
        destination_path = os.path.join(destination_dir, filename)

        try:
            os.makedirs(destination_dir, exist_ok=True)
            shutil.copy2(source_path, destination_path)
        except Exception as e:
            print(f"[Ошибка копирования изображения]: {e}")