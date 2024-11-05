import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import CartAddProductForm
from catalog.models import Product


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            product=product,
            quantity=cd['quantity'],
            price=cd['price'],
            update_quantity=cd['update']
        )
    return JsonResponse(cart.to_json(key=product_id), safe=False)


@require_POST
def cart_sub(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.sub(
            product=product,
            quantity=cd['quantity']
        )
    return JsonResponse(cart.to_json(key=product_id), safe=False)


def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart.html', {'cart': cart})


def mini_cart_detail(request):
    cart = Cart(request)
    return render(request, 'components/cart/mini-cart.html', {'cart': cart})


def cart_amounts(request):
    cart = Cart(request)
    return render(request, 'components/cart/cart-amounts.html', {'cart': cart})
