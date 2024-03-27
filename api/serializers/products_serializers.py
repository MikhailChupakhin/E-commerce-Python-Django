from rest_framework import serializers

from orders.models import BuyInOneClick
from products.models import Product, ProductCategory, ProductSubCategory, Manufacturer, ProductCharacteristic, \
    AlterImage, FeaturedProducts, Basket, FeaturedSubcategory


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'quantity', 'image', 'slug', 'is_new',
                  'total_price', 'article_number', 'category', 'sub_category',
                  'manufacturer']


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'slug']


class ProductSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSubCategory
        fields = ['id', 'name', 'slug', 'parent_category', 'parent_category_slug']


class ProductBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSubCategory
        fields = ['id', 'name', 'description', 'slug', 'parent_category_slug', 'image']


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = '__all__'


class ProductCharacteristicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCharacteristic
        fields = '__all__'


class AlterImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlterImage
        fields = '__all__'


class FeaturedProductsSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)

    class Meta:
        model = FeaturedProducts
        fields = ['products']


class BuyInOneClickSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyInOneClick
        fields = ['name', 'phone', 'email', 'product']

    def create(self, validated_data):
        return BuyInOneClick.objects.create(**validated_data)


class BasketAddSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1)


class BasketUpdateSerializer(serializers.Serializer):
    quantity_items = serializers.DictField(child=serializers.IntegerField(), required=False)
    removed_items = serializers.ListField(child=serializers.IntegerField(), required=False)


class BasketSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = Basket
        fields = '__all__'


class BasketCheckoutSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    quantity = serializers.IntegerField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, source='product.total_price')

    class Meta:
        model = Basket
        fields = ('product_name', 'quantity', 'total_price')


class BasketAnonymousSerializer(serializers.Serializer):
    quantity = serializers.IntegerField()


class BasketAnonymousUpdateSerializer(serializers.Serializer):
    quantity_items = serializers.DictField(child=serializers.DictField(child=serializers.IntegerField()), required=False)
    removed_items = serializers.ListField(child=serializers.IntegerField(), required=False)

    def to_representation(self, instance):
        return {
            'current_basket': [
                {
                    'quantity': data['quantity'],
                    'product': int(product_id)
                } for product_id, data in instance['quantity_items'].items()
            ] if 'quantity_items' in instance else []
        }


class FeaturedSubcategorySerializer(serializers.ModelSerializer):
    subcategory = serializers.SerializerMethodField()

    class Meta:
        model = FeaturedSubcategory
        fields = ['id', 'name', 'image', 'subcategory']

    def get_subcategory(self, obj):
        if obj.subcategory:
            parent_category_slug = obj.subcategory.parent_category.slug
            subcategory_slug = obj.subcategory.slug
            return f"/{parent_category_slug}/{subcategory_slug}"
        return None


class ProductQuickViewSerializer(serializers.ModelSerializer):
    characteristics = ProductCharacteristicSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'image', 'description', 'price', 'total_price', 'quantity', 'characteristics']