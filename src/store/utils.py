import json
from .models import *

def cookieCart(request):
    # Create empty cart for now for non-logged in user
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}

    print('CART:', cart)
    items = []
    order = {'get_cart_total': 0, 'get_quantity': 0, 'shipping': False}
    cartItems = order['get_quantity']

    for i in cart:
        try:
            cartItems += cart[i]["quantity"]
            product = Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])

            order['get_cart_total'] += total
            order['get_quantity'] += cart[i]['quantity']

            item = {
                'id': product.id,
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'imageUrl': product.imageUrl,
                },
                'quantity': cart[i]['quantity'],
                'get_total': total
            }

            items.append(item)

            if not product.digital:
                order['shipping'] = True
        except:
            pass
    return {'cartItems' : cartItems, 'order': order, 'items':items}


def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_quantity
    else:
        cookieData = cookieCart(request)
        items = cookieData['items']
        order = cookieData['order']
        cartItems = cookieData['cartItems']
    return {'cartItems' :cartItems, 'order': order, 'items':items}


def guestOrder(request, data):
    print('User is not logged in')

    print('COOKIES:', request.COOKIES)
    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    customer, created = Customer.objects.get_or_create(
        email=email,
    )

    customer.name = name
    customer.save()

    order = Order.objects.create(
        customer=customer,
        complete=False,
    )

    for item in items:
        product = Product.objects.get(id=item['id'])

        orderItem = OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity']
        )

    return customer, order