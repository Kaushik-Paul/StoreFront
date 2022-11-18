import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from storefront.responses import init_response, send_200, send_201, send_400, send_401, send_404
from store.models import Product, Collection, Review
from store.serializers import ProductSerializer, ReviewSerializer
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

