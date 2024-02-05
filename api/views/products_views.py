import json
from statistics import mean

from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_redis import get_redis_connection
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from orders.models import BuyInOneClick
from orders.tasks import send_notification_on_create
from reviews.models import ProductReview
from ..serializers.products_serializers import FeaturedProductsSerializer, ProductSerializer, \
    ProductSubCategorySerializer, ProductCategorySerializer, ManufacturerSerializer, BuyInOneClickSerializer, \
    BasketAddSerializer, BasketUpdateSerializer, BasketSerializer, \
    BasketAnonymousUpdateSerializer, FeaturedSubcategorySerializer
from ..serializers.reviews_serializers import ProductReviewSerializer
from ..serializers.seo_manager_serializers import InfoPageSerializer, SliderImageSerializer
from products.models import Basket, FeaturedProducts, Product, ProductCategory, Manufacturer, ProductSubCategory, \
    ComparisonList, FeaturedSubcategory
from seo_manager.models import InfoPage, SliderImage
from api.utils.breadcrumbs import get_breadcrumbs
from api.utils.seo_attributes import get_seo_attributes
from products.views import apply_filters_and_sort
from ..utils.misc import gt_check_get_cached_basket


class BaseAPIView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    def get_context(self):
        breadcrumbs_data = get_breadcrumbs(self.request)
        seo_data = get_seo_attributes(self.request)

        if self.request.user.is_authenticated:
            basket_items = Basket.objects.filter(user=self.request.user)
            total_items = sum(item.quantity for item in basket_items)
            products_in_cart = total_items
        else:
            basket_items = self.request.session.get('basket', {})
            products_in_cart = len(basket_items)

        categories = ProductCategory.objects.all()
        category_data = ProductCategorySerializer(categories, many=True).data

        subcategories_data = []
        for category in categories:
            subcategories = category.get_subcategories()
            subcategories_data.append(
                {
                    'category_name': category.name,
                    'subcategories_pack': ProductSubCategorySerializer(subcategories, many=True).data
                }
            )

        context = {
            "seo_data": seo_data,
            "breadcrumbs": breadcrumbs_data,
            "products_in_cart": products_in_cart,
            "categories": category_data,
            "subcategories": subcategories_data
        }
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context()
        return Response(data=context, status=status.HTTP_200_OK)


class IndexAPIView(BaseAPIView):
    def get(self, request, *args, **kwargs):
        context = {}

        base_response = super().get(request, *args, **kwargs)
        context.update(base_response.data)

        active_sliders = SliderImage.objects.filter(is_active=True)
        sliders_data = SliderImageSerializer(active_sliders, many=True).data
        context['sliders_and_banners'] = {'sliders': sliders_data, 'banners': []}

        index_banners = ProductSubCategory.objects.filter(is_index_banner=True)
        banners_data = ProductSubCategorySerializer(index_banners, many=True).data
        context['sliders_and_banners']['banners'] = banners_data

        featured_products = FeaturedProducts.objects.first()
        context['featured_products'] = FeaturedProductsSerializer(instance=featured_products).data.get('products')

        company_info = InfoPage.objects.filter(section=1)
        clients_info = InfoPage.objects.filter(section=2)
        context['company_info'] = InfoPageSerializer(company_info, many=True).data
        context['clients_info'] = InfoPageSerializer(clients_info, many=True).data

        return Response(data=context, status=status.HTTP_200_OK)


class CustomPagination(PageNumberPagination):
    page_size = 16
    page_size_query_param = 'page_size'
    max_page_size = 100


class BaseProductListView(ListAPIView):

    serializer_class = ProductSerializer
    pagination_class = CustomPagination
    model = Product
    queryset = Product.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        return apply_filters_and_sort(queryset, self.request)

    def get_base_context(self, request):
        base_view = BaseAPIView(request=request)
        return base_view.get_context()

    def paginate_queryset_and_serialize(self, queryset, request):
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(page, many=True)
        total_pages = paginator.page.paginator.num_pages
        current_page = paginator.page.number

        return serializer.data, queryset.count(), paginator.get_paginated_response, total_pages, current_page

    def list(self, request, *args, **kwargs):
        context = {}
        base_context = self.get_base_context(request)
        context.update(base_context)

        pagination_parameter = self.request.META.get('HTTP_PAGINATIONPARAM', '16')

        try:
            self.pagination_class.page_size = int(pagination_parameter)
        except:
            self.pagination_class.page_size = 16

        manufacturers_serializer = ManufacturerSerializer(Manufacturer.objects.all(), many=True)
        manufacturers_data = manufacturers_serializer.data

        queryset = self.filter_queryset(self.get_queryset())
        serialized_data, products_count, paginated_response, total_pages, current_page = self.paginate_queryset_and_serialize(queryset, request)

        context.update({
            'manufacturers': manufacturers_data,
            'product_list': serialized_data,
            'products_count': products_count,
            'total_pages': total_pages,
            'current_page': current_page,
        })

        if products_count == 0:
            featured_subcategories = FeaturedSubcategory.objects.all()

            featured_subcategories_data = FeaturedSubcategorySerializer(featured_subcategories, many=True).data
            context['featured_subcategories'] = featured_subcategories_data

        response = paginated_response(context) if paginated_response else Response(context)

        return response

    
class ProductsListAPIView(BaseProductListView):
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination
    queryset = Product.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


class CategoryProductsListAPIView(BaseProductListView):
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.kwargs.get('category_slug')
        category = get_object_or_404(ProductCategory, slug=category_slug)

        queryset = apply_filters_and_sort(queryset.filter(category=category), self.request)

        return queryset


class SubcategoryProductsListAPIView(BaseProductListView):
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.kwargs.get('category_slug')
        subcategory_slug = self.kwargs.get('subcategory_slug')
        sub_category = get_object_or_404(ProductSubCategory, slug=subcategory_slug)

        queryset = apply_filters_and_sort(queryset.filter(sub_category=sub_category), self.request)

        return queryset


class TagProductsAPIView(BaseProductListView):
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        tag_slug = self.kwargs['tag_slug']

        cache_key = f'tag_products_{tag_slug}_queryset'
        queryset = cache.get(cache_key)

        if queryset is None:
            queryset = Product.objects.filter(tags__slug=tag_slug)
            cache.set(cache_key, queryset, 3600)

        return queryset


class ProductSearchAPIView(BaseProductListView):
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        keyword = self.request.GET.get('keyword')
        if keyword:
            cache_key = f"product_search_{keyword}"

            cached_queryset = cache.get(cache_key)

            if cached_queryset is None:
                products = Product.objects.filter(
                    Q(name__icontains=keyword) |
                    Q(category__name__icontains=keyword) |
                    Q(sub_category__name__icontains=keyword)
                ).order_by('name').prefetch_related('characteristics')
                cached_queryset = products
                cache.set(cache_key, cached_queryset, 3600)

            return cached_queryset
        else:
            return Product.objects.none()


class DiscountedProductsAPIView(BaseProductListView):
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        cache_key = "discounted_products"

        cached_queryset = cache.get(cache_key)

        if cached_queryset is None:
            products = Product.objects.filter(discount_percentage__gt=0)
            cached_queryset = products
            cache.set(cache_key, cached_queryset, 3600)

        return cached_queryset


class ProductDetailAPIView(BaseAPIView):
    def get(self, request, *args, **kwargs):
        data = {}
        base_context = self.get_context()
        data.update(base_context)

        product_slug = kwargs.get('product_slug')
        product_id = kwargs.get('product_id')

        product = get_object_or_404(Product, id=product_id)

        product_serializer = ProductSerializer(product)

        reviews = ProductReview.objects.filter(product=product, moderated=True)
        reviews_serializer = ProductReviewSerializer(reviews, many=True)

        average_rating = mean(review.rating for review in reviews) if reviews else None

        viewed_product_ids = request.session.get('viewed_products', [])
        current_product_id = product.id

        if current_product_id not in viewed_product_ids:
            viewed_product_ids.append(current_product_id)
            request.session['viewed_products'] = viewed_product_ids

        viewed_products = Product.objects.filter(id__in=viewed_product_ids).exclude(id=product.id)[:10]

        similar_products = Product.objects.filter(sub_category=product.sub_category).exclude(
            id__in=viewed_product_ids).exclude(id=product.id)[:10]

        # !!! Определиться с механизмами персональных рекомендаций
        recommended_products = Product.objects.exclude(id__in=viewed_product_ids).exclude(
            id__in=similar_products.values_list('id', flat=True))[:10]

        data.update({
            'product': product_serializer.data,
            'reviews': reviews_serializer.data,
            'average_rating': average_rating,
            'viewed_products': ProductSerializer(viewed_products, many=True).data,
            'similar_products': ProductSerializer(similar_products, many=True).data,
            'recommended_products': ProductSerializer(recommended_products, many=True).data,
        })

        return Response(data, status=status.HTTP_200_OK)


class BuyInOneClickAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # TEST JSON {"name":"test", "phone":"8912345678", "email":"test@test.ru", "product":1}
        serializer = BuyInOneClickSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'success'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'status': 'error', 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@receiver(post_save, sender=BuyInOneClick)
def send_buyinoneclick_notification(sender, instance, created, **kwargs):
    if created:
        message_text = f"Заказ в 1 клик! ID: {instance.id} Дата: {instance.created.strftime('%Y-%m-%d %H:%M')} Email: {instance.email}"
        send_notification_on_create.apply_async(args=[message_text])


class BasketAddAPIView(APIView):
    # {"product_id": 1, "quantity": 2}
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = BasketAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data.get('quantity', 1)

        try:
            product = get_object_or_404(Product, id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Продукт не найден.'}, status=status.HTTP_404_NOT_FOUND)

        if quantity < 1:
            return Response({'error': 'Некорректное количество товара.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            basket = Basket.objects.get(user=request.user, product=product)
            total_quantity_in_basket = basket.quantity + quantity
            if total_quantity_in_basket > product.quantity:
                basket.quantity = product.quantity
                basket.save()
                message = f'Максимальное доступное количество товара ({product.quantity}) добавлено в корзину.'
            else:
                basket.quantity = total_quantity_in_basket
                basket.save()
                message = 'Количество товара обновлено в корзине.'
        except Basket.DoesNotExist:
            if quantity > product.quantity:
                quantity = product.quantity
            Basket.objects.create(user=request.user, product=product, quantity=quantity)
            message = 'Товар добавлен в корзину.'

        response_data = {
            'message': message,
            'available_quantity': product.quantity,
            'added_quantity': quantity,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class BasketAddAnonymousAPIView(APIView):
    # {"product_id": 1, "quantity": 2}

    def post(self, request):
        serializer = BasketAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        guest_token, redis_connection, basket_data = gt_check_get_cached_basket(request)

        product_id = serializer.validated_data['product_id']
        incoming_quantity = serializer.validated_data.get('quantity', 1)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'message': 'Продукт не найден.'}, status=status.HTTP_404_NOT_FOUND)

        if str(product_id) in basket_data.keys():
            basket_item = product_id
            basket_item_quantity = basket_data.get(str(product_id))
        else:
            basket_item = None
            basket_item_quantity = 0

        if basket_item:
            total_quantity_in_basket = basket_item_quantity + incoming_quantity
            if total_quantity_in_basket > product.quantity:
                outgoing_quantity = product.quantity
                message = f'Максимальное доступное количество товара ({product.quantity}) добавлено в корзину.'
            else:
                outgoing_quantity = total_quantity_in_basket
                message = 'Количество товара обновлено в корзине.'
        else:
            if incoming_quantity <= product.quantity:
                outgoing_quantity = incoming_quantity
                message = 'Товар добавлен в корзину.'
            else:
                outgoing_quantity = product.quantity
                message = f'Максимальное доступное количество товара ({outgoing_quantity}) добавлено в корзину.'

        basket_data[str(product_id)] = outgoing_quantity
        redis_connection.set(guest_token, json.dumps(basket_data), ex=3600)

        response_data = {
            'message': message,
            'available_quantity': product.quantity,
            'added_quantity': outgoing_quantity,
        }
        print(f'Response DATA:{response_data}')
        print(basket_data)
        return Response(response_data, status=status.HTTP_200_OK)


# class BasketUpdateAPIView(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request, *args, **kwargs):
#         baskets = Basket.objects.filter(user=request.user)
#         serializer = BasketSerializer(baskets, many=True)
#         return Response({'current_basket': serializer.data}, status=status.HTTP_200_OK)
#
#     def post(self, request, *args, **kwargs):
#         serializer = BasketUpdateSerializer(data=request.data)
#
#         if serializer.is_valid():
#             quantity_items = serializer.validated_data.get('quantity_items', {})
#
#             for product_id, quantity in quantity_items.items():
#                 basket = get_object_or_404(Basket, user=request.user, product=product_id)
#                 if quantity <= basket.product.quantity:
#                     basket.quantity = quantity
#                     basket.save()
#                     message = 'Количество товара в корзине обновлено.'
#                 else:
#                     message = f'Максимальное доступное количество товара ({basket.product.quantity}) добавлено в корзину.'
#
#             baskets = Basket.objects.filter(user=request.user)
#
#             serializer = BasketSerializer(baskets, many=True)
#
#             response_data = {
#                 'message': message,
#                 'current_basket': serializer.data,
#             }
#
#             return Response(response_data, status=status.HTTP_200_OK)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class BasketRemoveAPIView(APIView):
#     # {"removed_items": [1]}
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request, *args, **kwargs):
#         serializer = BasketUpdateSerializer(data=request.data)
#
#         if serializer.is_valid():
#             removed_items = serializer.validated_data.get('removed_items', [])
#
#             for removed_basket_id in removed_items:
#                 basket = get_object_or_404(Basket, user=request.user, product=removed_basket_id)
#                 basket.delete()
#
#             if request.user.is_authenticated:
#                 baskets = Basket.objects.filter(user=request.user)
#             else:
#                 basket_data = request.session.get('basket', {})
#                 basket_ids = list(map(int, basket_data.keys()))
#                 baskets = Basket.objects.filter(id__in=basket_ids)
#
#             serializer = BasketSerializer(baskets, many=True)
#
#             message = 'Товар был удален из корзины'
#             response_data = {
#                 'message': message,
#                 'current_basket': serializer.data,
#             }
#
#             return Response(response_data, status=status.HTTP_200_OK)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class BasketAnonymousUpdateAPIView(APIView):
#     # {
#     #     "quantity_items": {
#     #         "1": {
#     #             "quantity": 3
#     #         }
#     #     }
#     # }
#     def get(self, request, *args, **kwargs):
#         basket_data = request.session.get('basket', {})
#         serializer = BasketAnonymousUpdateSerializer(instance={'quantity_items': basket_data})
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     def post(self, request, *args, **kwargs):
#         serializer = BasketAnonymousUpdateSerializer(data=request.data)
#
#         if serializer.is_valid():
#             quantity_items = serializer.validated_data.get('quantity_items', {})
#
#             for product_id, quantity_data in quantity_items.items():
#                 basket_data = request.session.get('basket', {})
#
#                 if product_id in basket_data:
#                     product = Product.objects.get(id=product_id)
#                     basket_quantity = basket_data[product_id].get('quantity', 0)
#                     new_quantity = quantity_data.get('quantity', 0)
#                     if new_quantity <= product.quantity:
#                         basket_data[product_id]['quantity'] = new_quantity
#                         message = f'Количество товара в корзине изменено.'
#                     else:
#                         message = f'Максимальное доступное количество товара ({basket_quantity}) добавлено в корзину.'
#                 else:
#                     message = f'Товар с id {product_id} не найден в корзине.'
#
#                 request.session['basket'] = basket_data
#
#             basket_data = request.session.get('basket', {})
#
#             response_data = {
#                 'message': message,
#                 'current_basket': [
#                     {
#                         'quantity': data['quantity'],
#                         'product': int(product_id)
#                     } for product_id, data in basket_data.items()
#                 ],
#             }
#
#             return Response(response_data, status=status.HTTP_200_OK)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class BasketAnonymousRemoveAPIView(APIView):
#     # {
#     #     "removed_items": [1, 2, 3]
#     # }
#     def get(self, request, *args, **kwargs):
#         basket_data = request.session.get('basket', {})
#         serializer = BasketAnonymousUpdateSerializer(instance={'quantity_items': basket_data})
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     def post(self, request, *args, **kwargs):
#         serializer = BasketAnonymousUpdateSerializer(data=request.data)
#
#         if serializer.is_valid():
#             removed_items = serializer.validated_data.get('removed_items', [])
#
#             basket_data = request.session.get('basket', {})
#             for removed_basket_id in removed_items:
#                 if removed_basket_id in basket_data:
#                     del basket_data[removed_basket_id]
#
#             request.session['basket'] = basket_data
#
#             basket_data = request.session.get('basket', {})
#
#             message = 'Товар был удален из корзины'
#             response_data = {
#                 'message': message,
#                 'current_basket': [
#                     {
#                         'quantity': data['quantity'],
#                         'product': int(product_id)
#                     } for product_id, data in basket_data.items()
#                 ],
#             }
#
#             return Response(response_data, status=status.HTTP_200_OK)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeComparisonAPIView(APIView):
    # {"product_id": 1}
    def get(self, request):
        session = request.session
        session_id = session.session_key

        if not session_id:
            session.save()
            session_id = session.session_key

        try:
            comparison_list = ComparisonList.objects.get(session_id=session_id)
        except ComparisonList.DoesNotExist:
            comparison_list = ComparisonList.objects.create(session_id=session_id)

        serializer = ProductSerializer(comparison_list.products.all(), many=True)
        return Response({'products': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        session_id = request.session.session_key
        product_id = request.data.get('product_id')
        try:
            comparison_list = ComparisonList.objects.get(session_id=session_id)
        except ComparisonList.DoesNotExist:
            comparison_list = ComparisonList.objects.create(session_id=session_id)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'message': 'Товар не найден'}, status=status.HTTP_404_NOT_FOUND)

        if product in comparison_list.products.all():
            comparison_list.products.remove(product)
            message = 'Товар удален из списка для сравнения'
        else:
            if comparison_list.products.count() == 3:
                return Response({'message': 'Превышено максимальное количество товаров для сравнения'}, status=status.HTTP_400_BAD_REQUEST)

            comparison_list.products.add(product)
            message = 'Товар добавлен для сравнения'

        serializer = ProductSerializer(comparison_list.products.all(), many=True)
        return Response({'message': message, 'product_count': comparison_list.products.count(), 'products': serializer.data}, status=status.HTTP_200_OK)


class ComparisonAPIView(APIView):
    def get(self, request):
        session_id = request.session.session_key
        try:
            comparison_list = ComparisonList.objects.get(session_id=session_id)
            products = comparison_list.products.all()

            response_data = []
            for product in products:
                product_data = {
                    'product': ProductSerializer(product).data,
                    'product_characteristics': {},
                }

                characteristics = product.characteristics.all()
                for characteristic in characteristics:
                    product_data['product_characteristics'][characteristic.name] = characteristic.value

                response_data.append(product_data)

        except ComparisonList.DoesNotExist:
            response_data = []

        return Response({'products': response_data}, status=status.HTTP_200_OK)
