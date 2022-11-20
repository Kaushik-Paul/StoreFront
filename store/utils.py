from django.db import transaction
from store.models import CartItem, Product, Cart, Customer, Order, CartItem, OrderItem


class CartItemUtils:
    @staticmethod
    def create_cart_item(product_id, quantity, cart):
        product = Product.objects.filter(pk=product_id).first()
        if not product:
            raise Product.DoesNotExist
        if quantity < 1:
            raise Exception("Quantity must be greater than or equal to 1")

        cart_item = CartItem.objects.filter(product=product).first()
        if cart_item:
            cart_item.quantity += quantity
            cart_item.save()
            return cart_item
        else:
            return CartItem.objects.create(product=product, quantity=quantity, cart=cart)


class OrderItemUtils:
    @staticmethod
    def create_order(cart_id, user):
        with transaction.atomic():
            cart = Cart.objects.filter(pk=cart_id).first()
            if not cart:
                raise Cart.DoesNotExist
            if CartItem.objects.filter(cart=cart).count() == 0:
                raise Exception("Cart Item is Empty")
            customer, created = Customer.objects.get_or_create(user=user)
            order = Order.objects.create(customer=customer)
            OrderItemUtils.create_order_items(cart, order)
            cart.delete()
            return order

    @staticmethod
    def create_order_items(cart, order):
        cart_items = CartItem.objects.filter(cart=cart).select_related("product")
        order_items = []
        for cart_item in cart_items:
            order_item = OrderItem(
                product=cart_item.product,
                order=order,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.unit_price
            )
            order_items.append(order_item)
        OrderItem.objects.bulk_create(order_items)

