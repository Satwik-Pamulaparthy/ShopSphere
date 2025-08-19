from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Product, Order, OrderItem
from .forms import RegisterForm

def product_list(request):
    q = request.GET.get('q', '')
    products = Product.objects.all().order_by('-id')
    if q:
        products = products.filter(name__icontains=q)
    return render(request, 'store/product_list.html', {'products': products, 'q': q})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})

def _get_cart(request):
    return request.session.setdefault('cart', {})

def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = _get_cart(request)
    key = str(pk)
    if key in cart:
        cart[key]['qty'] += 1
    else:
        cart[key] = {'name': product.name, 'price': str(product.price), 'qty': 1}
    request.session.modified = True
    return redirect('store:view_cart')

def view_cart(request):
    cart = _get_cart(request)
    items = []
    total = Decimal('0.00')
    for pid, info in cart.items():
        price = Decimal(info['price'])
        qty = int(info['qty'])
        subtotal = price * qty
        total += subtotal
        items.append({'id': pid, 'name': info['name'], 'price': price, 'qty': qty, 'subtotal': subtotal})
    return render(request, 'store/cart.html', {'items': items, 'total': total})

def update_cart(request, pk, action):
    cart = _get_cart(request)
    key = str(pk)
    if key in cart:
        if action == 'inc':
            cart[key]['qty'] += 1
        elif action == 'dec':
            cart[key]['qty'] = max(1, cart[key]['qty'] - 1)
        elif action == 'del':
            del cart[key]
        request.session.modified = True
    return redirect('store:view_cart')

@login_required
def checkout(request):
    cart = _get_cart(request)
    if not cart:
        return redirect('store:product_list')

    total = Decimal('0.00')
    for info in cart.values():
        total += Decimal(info['price']) * int(info['qty'])

    order = Order.objects.create(user=request.user, total=total)
    for pid, info in cart.items():
        product = get_object_or_404(Product, pk=int(pid))
        OrderItem.objects.create(order=order, product=product, qty=int(info['qty']), price=Decimal(info['price']))
    request.session['cart'] = {}
    return render(request, 'store/checkout_success.html', {'order': order})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('store:product_list')
    else:
        form = RegisterForm()
    return render(request, 'store/register.html', {'form': form})

# Minimal JSON API for relevance to SDE roles
def api_products(request):
    data = list(Product.objects.values('id','name','description','price','image_url','category'))
    return JsonResponse(data, safe=False)
