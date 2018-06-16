from rest_framework import serializers

from base.models import Category, Product


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = '__all__'

    def get_products(self, obj):
        products = obj.product_set.all()
        serializer = ProductSerializer(products, many=True)
        return serializer.data