from decimal import Decimal
from itertools import product

from rest_framework import serializers

from store.models import Product, Collection, Review


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ["title", "feature_product"]


class ProductSerializer(serializers.ModelSerializer):
    total_tax_price = serializers.SerializerMethodField()
    collection = serializers.SerializerMethodField()

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
