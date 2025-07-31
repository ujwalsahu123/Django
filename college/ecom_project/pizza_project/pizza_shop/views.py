from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Pizza, Cart, CartItem, Order, OrderItem
from .ai_chat import get_ai_response

def home(request):
    pizzas = Pizza.objects.filter(is_available=True)
    return render(request, 'pizza_shop/home.html', {'pizzas': pizzas})

def chatbot(request):
    if request.method == 'POST':
        message = request.POST.get('message', '')
        response = get_ai_response(message)
        return JsonResponse({'response': response})
    return JsonResponse({'error': 'Invalid request method'})

def pizza_detail(request, pizza_id):
    pizza = get_object_or_404(Pizza, id=pizza_id)
    return render(request, 'pizza_shop/pizza_detail.html', {'pizza': pizza})

@login_required
def add_to_cart(request, pizza_id):
    if request.method == 'POST':
        pizza = get_object_or_404(Pizza, id=pizza_id)
        if not pizza.is_available:
            messages.error(request, 'Sorry, this pizza is currently unavailable.')
            return redirect('home')
            
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, pizza=pizza)
        
        quantity = int(request.POST.get('quantity', 1))
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
        
        messages.success(request, f'{quantity}x {pizza.name} added to cart!')
        return redirect('cart_detail')

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'pizza_shop/cart.html', {'cart': cart})

@login_required
def update_cart(request, item_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 0))
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
            
        return redirect('cart_detail')

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    # Check if cart is empty
    if not cart.cartitem_set.exists():
        messages.error(request, 'Your cart is empty!')
        return redirect('cart_detail')
    
    if request.method == 'POST':
        address = request.POST.get('address', '').strip()
        phone = request.POST.get('phone', '').strip()
        
        # Validate input
        if not address or not phone:
            messages.error(request, 'Please provide both delivery address and phone number.')
            return render(request, 'pizza_shop/checkout.html', {'cart': cart})
        
        try:
            # Create order from cart
            order = Order.objects.create(
                user=request.user,
                delivery_address=address,
                phone_number=phone,
                total_amount=cart.total,
                status='CONFIRMED'
            )
            
            # Create order items from cart items
            for cart_item in cart.cartitem_set.all():
                if not cart_item.pizza.is_available:
                    messages.error(request, f'Sorry, {cart_item.pizza.name} is no longer available.')
                    order.delete()
                    return redirect('cart_detail')
                    
                OrderItem.objects.create(
                    order=order,
                    pizza=cart_item.pizza,
                    quantity=cart_item.quantity,
                    price=cart_item.pizza.price
                )
            
            # Clear the cart
            cart.delete()
            messages.success(request, 'Order placed successfully! Your order is being prepared.')
            return redirect('order_detail', order_id=order.id)
            
        except Exception as e:
            messages.error(request, 'An error occurred while processing your order. Please try again.')
            if 'order' in locals():
                order.delete()
            return redirect('cart_detail')
    
    return render(request, 'pizza_shop/checkout.html', {'cart': cart})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'pizza_shop/order_detail.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'pizza_shop/order_history.html', {'orders': orders})
