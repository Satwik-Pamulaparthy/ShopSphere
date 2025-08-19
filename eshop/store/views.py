from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Product, Order, OrderItem
from .forms import RegisterForm

def product_list(request):
    q = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')  # NEW: Get selected category
    products = Product.objects.all().order_by('-id')

    if q:
        products = products.filter(name__icontains=q)
    if category_filter:
        products = products.filter(category=category_filter)

    # Get unique categories
    categories = Product.objects.values_list('category', flat=True).distinct()

    context = {
        'products': products,
        'q': q,
        'categories': categories,  # Pass categories to template
        'selected_category': category_filter,  # Highlight selected category
    }
    return render(request, 'store/product_list.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})

def _get_cart(request):
    return request.session.setdefault('cart', {})

# Require login before adding to cart
@login_required(login_url='store:login')
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = _get_cart(request)
    key = str(pk)
    if key in cart:
        cart[key]['qty'] += 1
    else:
        cart[key] = {'name': product.name, 'price': str(product.price), 'qty': 1}
    request.session.modified = True
    return redirect('store:product_list')

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

def api_products(request):
    data = list(Product.objects.values('id','name','description','price','image_url','category'))
    return JsonResponse(data, safe=False)

# ===============================
# NEW: API for the cart drawer
# ===============================
def api_cart(request):
    """
    Returns the current session cart as JSON for the slide-over drawer.
    Structure:
      {
        "items":[{"id":1,"name":"...","price":1.23,"qty":2,"subtotal":2.46,"image_url":"..."}],
        "total": 12.34,
        "count": 3
      }
    """
    cart = request.session.get('cart', {})
    items = []
    total = Decimal('0.00')

    for pid, info in cart.items():
        # Safe parsing
        price = Decimal(str(info.get('price', '0')))
        qty = int(info.get('qty', 0))
        subtotal = price * qty
        total += subtotal

        # Try to enrich from DB (handles deleted products gracefully)
        prod = Product.objects.filter(pk=int(pid)).first()
        items.append({
            'id': int(pid),
            'name': (prod.name if prod else info.get('name')),
            'price': float(price),
            'qty': qty,
            'subtotal': float(subtotal),
            'image_url': getattr(prod, 'image_url', None),
        })

    return JsonResponse({
        'items': items,
        'total': float(total),
        'count': sum(int(i.get('qty', 0)) for i in cart.values()),
    })

# ===============================
# Logout view (handles GET/POST)
# ===============================
@login_required
def logout_view(request):
    # Log out regardless of method so a plain <a href> works
    logout(request)
    return redirect('store:product_list')
