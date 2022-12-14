from decimal import Decimal
from itertools import product

from rest_framework import serializers

from store.models import Product, Collection, Review, Cart, CartItem, Customer, Order, OrderItem, ProductImage


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ["title", "feature_product"]


class ProductImageSerializer(serializers.ModelSerializer):
    product_title = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = [
            "id",
            "product_title",
            "image"
        ]

    def get_product_title(self, product_image):
        return product_image.product.title


class ProductSerializer(serializers.ModelSerializer):
    total_tax_price = serializers.SerializerMethodField()
    collection = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "unit_price",
            "inventory",
            "total_tax_price",
            "collection",
            "images",
        ]

    def get_total_tax_price(self, product):
        return product.unit_price * Decimal(10)

    def get_collection(self, product):
        return product.collection.title


class ReviewSerializer(serializers.ModelSerializer):
    product_title = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "name",
            "description",
            "product_title"
        ]

    def get_product_title(self, review):
        return review.product.title


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Cart
        fields = [
            "id",
        ]


class CartDetailsSerializer(serializers.ModelSerializer):
    cart_id = serializers.UUIDField(source="id")
    items = serializers.SerializerMethodField(read_only=True)
    grand_total = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Cart
        fields = [
            "cart_id",
            "items",
            "grand_total",
        ]

    def get_items(self, cart):
        cart_items = cart.items.all()
        return CartItemSerializer(cart_items, many=True).data

    def get_grand_total(self, cart):
        grand_total = 0
        cart_items = cart.items.all()
        for cart_item in cart_items:
            cart_item_price = cart_item.total_price
            grand_total += cart_item_price
        return f"Rs {grand_total}"


class CartItemSerializer(serializers.ModelSerializer):
    cart_item_id = serializers.IntegerField(source="id")
    product = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "cart_item_id",
            "product",
            "total_price",
            "quantity"
        ]

    def get_product(self, cart_item):
        product = cart_item.product
        data = {
            "product_title": product.title,
            "product_unit_price": product.unit_price,
            "product_quantity": cart_item.quantity,
        }
        return data

    def get_total_price(self, cart_item):
        return cart_item.total_price


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()

    class Meta:
        model = Customer
        fields = [
            "id",
            "user_id",
            "phone",
            "birth_date",
            "membership",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    order_item_id = serializers.IntegerField(source="id")

    class Meta:
        model = OrderItem
        fields = [
            "order_item_id",
            "quantity",
            "unit_price",
            "product"
        ]

    def get_product(self, order_item):
        product = order_item.product
        data = {
            "product_id": product.id,
            "product_title": product.title,
            "product_unit_price": product.unit_price,
        }
        return data


class OrderSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source="id")
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "order_id",
            "customer",
            "placed_at",
            "payment_status",
            "items"
        ]


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["payment_status"]
