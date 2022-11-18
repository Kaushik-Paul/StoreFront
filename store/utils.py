from store.models import CartItem, Product


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
