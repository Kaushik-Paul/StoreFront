import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from storefront.responses import init_response, send_200, send_201, send_204, send_400, send_401, send_404
from store.models import Product, Collection, Review, Cart, CartItem
from store.serializers import ProductSerializer, ReviewSerializer, CartSerializer, CartDetailsSerializer, CartItemSerializer
from store.utils import CartItemUtils
import logging
logger = logging.getLogger("storefront")


class ProductList(APIView):
    def __init__(self):
        self.response = init_response(
            response_string="Product List fetched successfully!!"
        )

    def get(self, request):
        collection_id = request.query_params.get("collection_id")
        queryset = Product.objects.all()
        if collection_id:
            queryset = queryset.filter(collection_id=collection_id)
        products = queryset
        product_serializer = ProductSerializer(products, many=True)
        self.response["response_data"] = product_serializer.data
        return send_200(self.response)

    def post(self, request):
        data = request.data
        product = Product.objects.create(**data)
        self.response["response_string"] = "Product Created Successfully"
        self.response["response_data"] = ProductSerializer(product).data
        return send_201(data=self.response)


class ProductDetail(APIView):
    def __init__(self):
        self.response = init_response(
            response_string="Product Details fetched successfully!!"
        )

    def get(self, request, product_id):
        product = Product.objects.filter(pk=product_id).first()
        if not product:
            self.response["response_string"] = "Product is Not Available"
            return send_404(data=self.response)
        product_serializer = ProductSerializer(product)
        self.response["response_data"] = product_serializer.data
        return send_200(self.response)

    def put(self, request, product_id):
        product = Product.objects.filter(pk=product_id).first()
        if not product:
            self.response["response_string"] = "Product is Not Available"
            return send_404(data=self.response)
        data = request.data
        # updated_product = Product.objects.filter(pk=product_id).update(**data)
        for key in data:
            setattr(product, key, data[key])
        product.save()
        self.response["response_string"] = "Product Updated Successfully!!"
        self.response["response_data"] = ProductSerializer(product).data
        return send_200(data=self.response)


class ReviewList(APIView):
    def __init__(self):
        self.response = init_response(
            response_string="Review List fetched successfully!!"
        )

    def get(self, request, product_id):
        reviews = Review.objects.filter(product=product_id).all()
        self.response["response_data"] = ReviewSerializer(reviews, many=True).data
        return send_200(self.response)

    def post(self, request, product_id):
        product = Product.objects.filter(pk=product_id).first()
        if not product:
            self.response["response_string"] = "Product Not Found !!"
            return send_404(data=self.response)

        # TODO: Look into it ??
        review = Review.objects.create(**request.data)
        review.product = product
        review.save()
        self.response["response_string"] = "Review for the Product Created Successfully"
        self.response["response_data"] = ReviewSerializer(review).data
        return send_201(data=self.response)


class ReviewDetail(APIView):
    def __init__(self):
        self.response = init_response(
            response_string="Review Details fetched successfully!!"
        )

    def get(self, request, product_id, review_id):
        review = Review.objects.filter(pk=review_id, product_id=product_id).first()
        if not review:
            self.response["response_string"] = "Review Not Found !!"
            return send_404(data=self.response)
        review_serializer = ReviewSerializer(review)
        self.response["response_data"] = review_serializer.data
        return send_200(self.response)

    def put(self, request, product_id, review_id):
        review = Review.objects.filter(pk=review_id, product_id=product_id).first()
        if not review:
            self.response["response_string"] = "Review Not Found !!"
            return send_404(data=self.response)
        data = request.data
        for key in data:
            setattr(review, key, data[key])
        review.save()
        self.response["response_string"] = "Review Updated Successfully!!"
        self.response["response_data"] = ReviewSerializer(review).data
        return send_200(data=self.response)


class CreateCart(APIView):
    def __init__(self):
        self.response = init_response(
            response_string="Cart created successfully !!"
        )

    def post(self, request):
        cart = Cart.objects.create()
        cart_serializer = CartSerializer(cart).data
        self.response["response_data"] = cart_serializer
        return send_200(self.response)


class CartDetailView(APIView):
    def __init__(self):
        self.response = init_response(
            response_string="Cart Details Fetched successfully !!"
        )

    def get(self, request, cart_id):
        cart = Cart.objects.filter(pk=cart_id).prefetch_related("items__product").first()
        if not cart:
            self.response["response_string"] = "Cart Not Found !!"
            return send_404(data=self.response)
        cart_data = CartDetailsSerializer(cart)
        self.response["response_data"] = cart_data.data
        return send_200(self.response)

    def delete(self, request, cart_id):
        cart = Cart.objects.filter(pk=cart_id).prefetch_related("items__product").first()
        if not cart:
            self.response["response_string"] = "Cart Not Found !!"
            return send_404(data=self.response)
        cart.delete()
        self.response["response_string"] = "Cart Deleted Successfully !!"
        return send_204(self.response)


class CartItemsView(APIView):
    def __init__(self):
        self.response = init_response(
            response_string="Cart Items List Fetched successfully !!"
        )

    def get(self, request, cart_id):
        cart = Cart.objects.filter(pk=cart_id).prefetch_related("items__product").first()
        if not cart:
            self.response["response_string"] = "Cart Not Found !!"
            return send_404(data=self.response)

        cart_items = cart.items.all()
        cart_items_serializer = CartItemSerializer(cart_items, many=True)
        self.response["response_data"] = cart_items_serializer.data
        return send_200(self.response)

    def post(self, request, cart_id):
        cart = Cart.objects.filter(pk=cart_id).prefetch_related("items__product").first()
        if not cart:
            self.response["response_string"] = "Cart Not Found !!"
            return send_404(data=self.response)
        data = request.data
        product_id = data.get("product_id")
        quantity = data.get("quantity")
        if not product_id or not quantity:
            self.response["response_string"] = "Both quantity and product_id is required"
            return send_400(data=self.response)
        try:
            cart_item = CartItemUtils.create_cart_item(product_id, quantity, cart)
            self.response["response_data"] = CartItemSerializer(cart_item).data
            return send_200(self.response)
        except Product.DoesNotExist as ex:
            logger.error(ex)
            self.response["response_string"] = "Product id is not valid"
            return send_400(self.response)
        except Exception as ex:
            logger.error(ex)
            self.response["response_string"] = ex
            return send_400(self.response)


class CartItemDetailsView(APIView):
    def __init__(self):
        self.response = init_response(
            response_string="Cart Item Details Fetched successfully !!"
        )

    def get(self, request, cart_id, cart_item_id):
        cart_item = CartItem.objects.filter(pk=cart_item_id, cart_id=cart_id).first()
        if not cart_item:
            self.response["response_string"] = "Cart Item Not Found !!"
            return send_404(data=self.response)
        cart_item_serializer = CartItemSerializer(cart_item)
        self.response["response_data"] = cart_item_serializer.data
        return send_200(self.response)

