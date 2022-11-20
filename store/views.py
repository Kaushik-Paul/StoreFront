import json
from django_filters.rest_framework import DjangoFilterBackend
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter

from store.filters import ProductFilter
from storefront.responses import init_response, send_200, send_201, send_204, send_400, send_401, send_404
from store.models import Product, Review, Cart, CartItem, Customer, Order
from store.permissions import IsAdminOrReadOnly, IsAdminOrReadOnlyForAuthenticated
from store.serializers import (ProductSerializer,
                               ReviewSerializer,
                               CartSerializer,
                               CartDetailsSerializer,
                               CartItemSerializer,
                               CustomerSerializer,
                               OrderSerializer,
                               UpdateOrderSerializer)
from store.utils import CartItemUtils, OrderItemUtils
import logging
logger = logging.getLogger("storefront")


class ProductList(APIView):
    # permission_classes = [IsAdminOrReadOnly]

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
        # Add Paginator
        page_no = int(request.query_params.get("page_number", 1))
        page_size = int(request.query_params.get("page_size", 2))
        paginator = Paginator(products, page_size)
        page_object = paginator.page(page_no)
        paginated_data = page_object.object_list
        product_serializer = ProductSerializer(paginated_data, many=True)

        self.response["response_data"] = product_serializer.data
        return send_200(self.response)

    def post(self, request):
        data = request.data
        product = Product.objects.create(**data)
        self.response["response_string"] = "Product Created Successfully"
        self.response["response_data"] = ProductSerializer(product).data
        return send_201(data=self.response)


class ProductDetail(APIView):
    permission_classes = [IsAdminOrReadOnly]

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

        review = Review.objects.create(**request.data, product=product)
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

    def patch(self, request, cart_id, cart_item_id):
        cart_item = CartItem.objects.filter(pk=cart_item_id, cart_id=cart_id).first()
        if not cart_item:
            self.response["response_string"] = "Cart Item Not Found !!"
            return send_404(data=self.response)
        data = request.data
        for key in data:
            setattr(cart_item, key, data[key])
        cart_item.save()
        self.response["response_string"] = "Cart Item Updated Successfully!!"
        self.response["response_data"] = CartItemSerializer(cart_item).data
        return send_200(data=self.response)

    def delete(self, request, cart_id, cart_item_id):
        cart_item = CartItem.objects.filter(pk=cart_item_id, cart_id=cart_id).first()
        if not cart_item:
            self.response["response_string"] = "Cart Item Not Found !!"
            return send_404(data=self.response)
        cart_item.delete()
        self.response["response_string"] = "Cart Item Deleted Successfully !!"
        return send_204(self.response)


class CreateCustomerView(APIView):
    def __init__(self):
        self.response = init_response(
            response_string="Customer Created Successfully !!"
        )

    def post(self, request):
        data = request.data
        customer_serializer = CustomerSerializer(data=data)
        if customer_serializer.is_valid():
            customer_serializer.save()
            self.response["response_data"] = customer_serializer.data
            return send_201(self.response)
        else:
            self.response["response_string"] = "Error while creating Customer"
            self.response["response_data"] = customer_serializer.errors
            return send_400(data=self.response)


class CustomerDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self):
        self.response = init_response(
            response_string="Customer Details Fetched Successfully !!"
        )

    def get(self, request):
        user = request.user
        customer = Customer.objects.filter(user_id=user.id).first()
        self.response["response_data"] = CustomerSerializer(customer).data
        return send_200(self.response)

    def put(self, request):
        user = request.user
        customer = Customer.objects.filter(user_id=user.id).first()
        data = request.data
        for key in data:
            setattr(customer, key, data[key])
        customer.save()
        self.response["response_string"] = "Customer Details Updated Successfully!!"
        self.response["response_data"] = CustomerSerializer(customer).data
        return send_200(data=self.response)


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self):
        self.response = init_response(
            response_string="Order List Fetched Successfully !!"
        )

    def get_queryset(self, user):
        if user.is_staff:
            return Order.objects.all()
        customer = Customer.objects.only("id").filter(user_id=user.id).first()
        return Order.objects.filter(customer=customer)

    def get(self, request):
        orders = self.get_queryset(request.user)
        self.response["response_data"] = OrderSerializer(orders, many=True).data
        return send_200(self.response)

    def post(self, request):
        try:
            user = request.user
            data = request.data
            cart_id = data.get("cart_id")
            if not cart_id:
                self.response["response_string"] = "Cart id is a mandatory field"
                return send_400(self.response)
            order = OrderItemUtils.create_order(cart_id, user)
            self.response["response_data"] = OrderSerializer(order).data
            self.response["response_string"] = "Order Created Successfully !!"
            return send_201(data=self.response)
        except Cart.DoesNotExist as ex:
            logger.error(ex)
            self.response["response_string"] = "Cart id is not valid"
            return send_400(self.response)
        except Exception as ex:
            logger.error(ex)
            self.response["response_string"] = ex
            return send_400(self.response)


class OrderDetailsView(APIView):
    permission_classes = [IsAdminOrReadOnlyForAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response = init_response(
            response_string="Order Details Fetched Successfully !!"
        )

    def get_queryset(self, user):
        if user.is_staff:
            return Order.objects.all()
        customer = Customer.objects.only("id").filter(user_id=user.id).first()
        return Order.objects.filter(customer=customer)

    def get(self, request, order_id):
        user = request.user
        order = self.get_queryset(user).filter(pk=order_id).first()
        if not order:
            self.response["response_string"] = "Order Not Found !!"
            return send_404(data=self.response)
        self.response["response_data"] = OrderSerializer(order).data
        return send_200(self.response)

    def patch(self, request, order_id):
        order = Order.objects.filter(pk=order_id).first()
        if not order:
            self.response["response_string"] = "Order Not Found !!"
            return send_404(data=self.response)
        data = request.data
        order_serializer = UpdateOrderSerializer(order, data=data)
        if order_serializer.is_valid():
            order_serializer.save()
            self.response["response_string"] = "Order Updated Successfully!!"
            self.response["response_data"] = OrderSerializer(order).data
            return send_200(data=self.response)
        else:
            self.response["response_string"] = "Order Updated Failed!!"
            self.response["response_data"] = order_serializer.errors
            return send_400(data=self.response)



