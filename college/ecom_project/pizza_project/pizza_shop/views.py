from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Pizza, Cart, CartItem, Order, OrderItem
from .ai_chat import get_ai_response
from .razorpay_utils import create_razorpay_order, verify_payment_signature

def home(request):
    pizzas = Pizza.objects.filter(is_available=True)
    return render(request, 'pizza_shop/home.html', {'pizzas': pizzas})

def chatbot(request):
    if request.method == 'POST':
        message = request.POST.get('message', '')
        response = get_ai_response(message)
        return JsonResponse({'response': response})
    return JsonResponse({'error': 'Invalid request method'})

@login_required
def initiate_payment(request, order_id):
    """
    Initiates the Razorpay payment
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.payment_status == 'PAID':
        messages.info(request, 'This order has already been paid for.')
        return redirect('order_detail', order_id=order.id)
    
    # Convert amount to paise (Razorpay expects amount in smallest currency unit)
    amount_in_paise = int(order.total_amount * 100)
    
    # Create Razorpay Order
    razorpay_order = create_razorpay_order(amount_in_paise)
    
    # Update order with Razorpay order ID
    order.razorpay_order_id = razorpay_order['id']
    order.save()
    
    # Prepare payment data for template
    payment_data = {
        'order_id': order.id,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount': amount_in_paise,
        'currency': settings.RAZORPAY_CURRENCY,
        'name': 'Pizza Shop',
        'description': f'Order #{order.id}',
        'customer_name': request.user.get_full_name() or request.user.username,
        'customer_email': request.user.email,
        'callback_url': request.build_absolute_uri(f'/payment/callback/'),
        'notes': {
            'merchant_order_id': str(order.id),
        },
        'theme': {
            'color': '#F37254'
        }
    }
    
    return render(request, 'pizza_shop/payment.html', {'payment_data': payment_data})

@csrf_exempt
def payment_callback(request):
    """
    Handles the payment callback from Razorpay
    """
    if request.method == 'POST':
        import json
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            razorpay_payment_id = data.get('razorpay_payment_id', '')
            razorpay_order_id = data.get('razorpay_order_id', '')
            razorpay_signature = data.get('razorpay_signature', '')
        except json.JSONDecodeError:
            # If not JSON, try POST data
            razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            razorpay_signature = request.POST.get('razorpay_signature', '')

        # For test mode, consider the payment valid if we have a payment ID
        is_valid = True if settings.RAZORPAY_TEST_MODE and razorpay_payment_id else verify_payment_signature(
            razorpay_payment_id,
            razorpay_order_id,
            razorpay_signature
        )
        
        # Get the order
        try:
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
        except Order.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Order not found'})
        
        if is_valid:
            # Update order status
            order.payment_status = 'PAID'
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signature = razorpay_signature
            order.status = 'CONFIRMED'
            order.save()
            
            messages.success(request, 'Payment successful! Your order has been confirmed.')
            return JsonResponse({'status': 'success', 'order_id': order.id})
        else:
            order.payment_status = 'FAILED'
            order.save()
            messages.error(request, 'Payment verification failed. Please try again.')
            return JsonResponse({'status': 'error', 'message': 'Payment verification failed'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

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
