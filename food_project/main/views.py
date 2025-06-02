from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from .forms import CustomUserCreationForm

from django.db import models

from .models import Product

User = get_user_model()


def home_view(request):
    products = Product.objects.all()
    return render(request, 'main/home.html', {'products': products})


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'main/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})

def is_admin(user):
    return user.is_authenticated and user.is_superuser  # или user.is_admin, если у тебя кастомная роль

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def cart_view(request):
    # Пример данных (в будущем заменим на реальные из базы данных или сессии)
    cart_items = request.session.get('cart', [])
    total = sum(item["price"] * item["quantity"] for item in cart_items)

    context = {
        "cart_items": cart_items,
        "total": total,
        "range": range(1, 11),  # вот это и используется в шаблоне
    }
    return render(request, 'main/cart.html', context)

@user_passes_test(is_admin)
def admin_panel_view(request):
    from .models import Product, User

    if request.method == 'POST':
        action = request.POST.get("action4")
        if action == "create":
            name = request.POST.get("product_name")
            price = request.POST.get("product_price")
            category = request.POST.get("category")
            image = request.FILES.get("product_image")

            if name and price and image:
                Product.objects.create(name=name, price=price, category=category, image=image)


        elif action == "delete":
            name = request.POST.get("product_name")
            if name:
                Product.objects.filter(name=name).delete()


        elif request.POST.get("courier_username"):
            # логика создания курьера
            username = request.POST.get("courier_username")
            password = request.POST.get("courier_password")

            if username and password:
                if not User.objects.filter(username=username).exists():
                    User.objects.create_user(username=username, password=password, is_courier=True)

    products = Product.objects.all()
    return render(request, "main/admin_panel.html", {"products": products})

@login_required
def courier_panel_view(request):
    from .models import Order

    if not request.user.is_courier:
        return redirect('home')

    if request.method == 'POST':
        order_id = request.POST.get("order_id")
        new_status = request.POST.get("status")
        try:
            order = Order.objects.get(id=order_id)
            order.status = new_status
            order.courier = request.user  # Назначаем курьера
            order.save()
        except Order.DoesNotExist:
            pass

    orders = Order.objects.filter(models.Q(courier=request.user) | models.Q(courier__isnull=True))
    return render(request, "main/courier_panel.html", {"orders": orders})

@require_POST
@login_required
def update_quantity_view(request, item_name):
    # Пример: обновляем количество товара в сессии (пока заглушка)
    quantity = int(request.POST.get('quantity', 1))
    cart = request.session.get('cart', [])

    for item in cart:
        if item['name'] == item_name:
            item['quantity'] = quantity
            break
    request.session['cart'] = cart
    return redirect('cart')

from .models import Product, Order, OrderItem

@login_required
def checkout_view(request):
    cart = request.session.get('cart', [])
    if not cart:
        return redirect('cart')

    # СОЗДАЁМ ЗАКАЗ
    order = Order.objects.create(
        user=request.user,
        courier=None  # Пока курьера нет — назначай вручную позже
    )

    for item in cart:
        try:
            product = Product.objects.get(name=item['name'])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity']
            )
        except Product.DoesNotExist:
            continue

    request.session['cart'] = []
    return redirect('cart')


@login_required
def clear_cart_view(request):
    request.session['cart'] = []
    return redirect('cart')

@require_POST
@login_required
def add_to_cart_view(request):
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return redirect('home')

    cart = request.session.get('cart', [])

    # Проверка — если товар уже есть, увеличить количество
    for item in cart:
        if item['name'] == product.name:
            item['quantity'] += quantity
            break
    else:
        cart.append({
            'name': product.name,
            'price': float(product.price),
            'quantity': quantity
        })

    request.session['cart'] = cart
    return redirect('cart')

@login_required
def my_orders_view(request):
    orders = request.user.orders.prefetch_related("items__product").order_by("-created_at")
    return render(request, "main/my_orders.html", {"orders": orders})
