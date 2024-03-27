import json
from statistics import mean

from django.db.models import Q, Min, Max, Exists, OuterRef
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
    BasketAnonymousUpdateSerializer, FeaturedSubcategorySerializer, ProductBannerSerializer, ProductQuickViewSerializer
from ..serializers.reviews_serializers import ProductReviewSerializer
from ..serializers.seo_manager_serializers import InfoPageSerializer, SliderImageSerializer, TagSerializer
from products.models import Basket, FeaturedProducts, Product, ProductCategory, Manufacturer, ProductSubCategory, \
    ComparisonList, FeaturedSubcategory
from seo_manager.models import InfoPage, SliderImage, Tag
from api.utils.breadcrumbs import get_breadcrumbs
from api.utils.seo_attributes import get_seo_attributes
from products.views import apply_filters_and_sort
from ..utils.misc import gt_check_get_cached_basket


class BaseAPIView(APIView):
    def get_context(self):

        # if self.request.user.is_authenticated:
        #     basket_items = Basket.objects.filter(user=self.request.user)
        #     total_items = sum(item.quantity for item in basket_items)
        #     products_in_cart = total_items
        # else:
        #     basket_items = self.request.session.get('basket', {})
        #     products_in_cart = len(basket_items)

        categories = ProductCategory.objects.all()
        category_data = ProductCategorySerializer(categories, many=True).data

        subcategories_data = []
        for category in categories:
            subcategories = category.get_subcategories()
            subcategories_data.append(
                {
                    'category_id': category.id,
                    'subcategories_pack': ProductSubCategorySerializer(subcategories, many=True).data
                }
            )

        context = {
            "categories": category_data,
            "subcategories": subcategories_data
        }
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context()
        return Response(data=context, status=status.HTTP_200_OK)


class IndexAPIView(APIView):
    def get(self, request, *args, **kwargs):
        context = {}
        seo_data = {'title': 'Index Default Title', 'meta-description': 'Index Default Descr'}
        context['seo_data'] = seo_data
        active_sliders = SliderImage.objects.filter(is_active=True)
        sliders_data = SliderImageSerializer(active_sliders, many=True).data
        context['sliders_and_banners'] = {'sliders': sliders_data, 'banners': []}

        index_banners = ProductSubCategory.objects.filter(is_index_banner=True)
        banners_data = ProductBannerSerializer(index_banners, many=True).data
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

    def paginate_queryset_and_serialize(self, queryset, request):
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(page, many=True)
        total_pages = paginator.page.paginator.num_pages
        current_page = paginator.page.number

        return serializer.data, queryset.count(), paginator.get_paginated_response, total_pages, current_page

    def list(self, request, *args, **kwargs):
        context = {}
        queryset, set_params = self.get_queryset(request, *args, **kwargs)
        breadcrumbs = get_breadcrumbs(set_params)
        seo_data = get_seo_attributes(set_params)
        context['breadcrumbs'] = breadcrumbs
        context['seo_data'] = seo_data

        pagination_parameter = self.request.META.get('HTTP_PAGINATIONPARAM', '16')

        try:
            self.pagination_class.page_size = int(pagination_parameter)
        except:
            self.pagination_class.page_size = 16


        manufacturers_serializer = ManufacturerSerializer((
            Manufacturer.objects
            .annotate(has_products=Exists(Product.objects.filter(manufacturer=OuterRef('pk'))))
            .filter(has_products=True)
            .order_by('name')
            .all()
        ), many=True)

        manufacturers_data = manufacturers_serializer.data

        price_range = Product.objects.aggregate(
            min_price=Min('total_price'),
            max_price=Max('total_price')
        )

        min_price = price_range.get('min_price', 0)
        max_price = price_range.get('max_price', 0)

        tags_serializer = TagSerializer(Tag.objects.all(), many=True)
        tags_data = tags_serializer.data
        # queryset, mixed_params = self.filter_queryset(self.get_queryset())
        serialized_data, products_count, paginated_response, total_pages, current_page = self.paginate_queryset_and_serialize(queryset, request)

        context.update({
            'manufacturers': manufacturers_data,
            'price_interval': {
                'min': min_price,
                'max': max_price
            },
            'tags_data': tags_data,
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


class TagProductsAPIView(BaseProductListView):
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination

    def get_set_params(self):
        url = self.request.path
        tag_slug = self.kwargs.get('tag_slug')
        tag = get_object_or_404(Tag, slug=tag_slug)
        return {'page_type': 'tag',
                'url': url,
                'tag_name': tag.name,
                'tag_id': tag.id}

    def get_queryset(self, *args, **kwargs):
        set_params = self.get_set_params()

        queryset = super().get_queryset()
        queryset = apply_filters_and_sort(queryset.filter(tags__id=set_params['tag_id']), self.request)

        return queryset, set_params

    
class ProductsListAPIView(BaseProductListView):
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination
    queryset = Product.objects.all()

    def get_queryset(self, *args, **kwargs):
        set_params = {'page_type': 'catalog', 'url': '/catalog'}
        queryset = super().get_queryset()
        return queryset, set_params


class CategoryProductsListAPIView(BaseProductListView):
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination

    def get_set_params(self):
        url = self.request.path
        category_slug = self.kwargs.get('category_slug')
        category = get_object_or_404(ProductCategory, slug=category_slug)
        return {'page_type': 'category',
                'url': url,
                'category_name': category.name,
                'category_id': category.id}

    def get_queryset(self, *args, **kwargs):
        set_params = self.get_set_params()
        queryset = super().get_queryset()
        queryset = apply_filters_and_sort(queryset.filter(category=set_params['category_id']), self.request)
        return queryset, set_params


class SubcategoryProductsListAPIView(BaseProductListView):
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination

    def get_set_params(self):
        url = self.request.path
        category_slug = self.kwargs.get('category_slug')
        category = get_object_or_404(ProductCategory, slug=category_slug)
        subcategory_slug = self.kwargs.get('subcategory_slug')
        subcategory = get_object_or_404(ProductSubCategory, slug=subcategory_slug)

        return {'page_type': 'subcategory',
                'url': url,
                'category_name': category.name,
                'category_slug': category.slug,
                'category_id': category.id,
                'subcategory_name': subcategory.name,
                'subcategory_slug': subcategory.slug,
                'subcategory_id': subcategory.id}

    def get_queryset(self, *args, **kwargs):
        set_params = self.get_set_params()
        queryset = super().get_queryset()
        queryset = apply_filters_and_sort(queryset.filter(sub_category=set_params['subcategory_id']), self.request)
        return queryset, set_params


class ProductSearchAPIView(BaseProductListView):
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        set_params = {'page_type': 'search', 'url': '/search'}
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

            return cached_queryset, set_params
        else:
            return Product.objects.none(), set_params


class DiscountedProductsAPIView(BaseProductListView):
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        set_params = {'page_type': 'discounts', 'url': '/discounts'}
        cache_key = "discounted_products"

        cached_queryset = cache.get(cache_key)

        if cached_queryset is None:
            products = Product.objects.filter(discount_percentage__gt=0)
            cached_queryset = products
            cache.set(cache_key, cached_queryset, 3600)

        return cached_queryset, set_params


class ProductQuickviewAPIView(APIView):
    def get(self, request, product_id, *args, **kwargs):
        print('ProductQuickviewAPIView called')
        data = {}

        product = get_object_or_404(Product, id=product_id)
        product_serializer = ProductQuickViewSerializer(product)

        data.update({
            'product': product_serializer.data,
        })

        return Response(data, status=status.HTTP_200_OK)


class ProductDetailAPIView(BaseAPIView):
    ''' Required refactory of Viewed Products logic (Redis cache?) '''
    def get_set_params(self):
        url = self.request.path
        product_id = self.kwargs.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        return {'page_type': 'product',
                'url': url,
                'category_name': product.category.name,
                'category_slug': product.category.slug,
                'subcategory_name': product.sub_category.name,
                'subcategory_slug': product.sub_category.slug,
                'product_name': product.name,
                'product_slug': product.slug,
                'product_id': product.id}

    def get(self, request, *args, **kwargs):
        data = {}
        set_params = self.get_set_params()
        base_context = self.get_context(set_params=set_params)
        data.update(base_context)

        product = get_object_or_404(Product, id=set_params['product_id'])
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

        '''Определиться с механизмом персональных рекомендаций'''
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
                code = 2
                message = f'Максимальное доступное количество товара ({product.quantity}) добавлено в корзину.'
            else:
                basket.quantity = total_quantity_in_basket
                basket.save()
                code = 1
                message = 'Количество товара обновлено в корзине.'
        except Basket.DoesNotExist:
            if quantity > product.quantity:
                quantity = product.quantity
            Basket.objects.create(user=request.user, product=product, quantity=quantity)
            code = 0
            message = 'Товар добавлен в корзину.'

        response_data = {
            'code': code,
            'message': message,
            'available_quantity': product.quantity,
            'added_quantity': quantity,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class BasketAddGuestAPIView(APIView):
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
                code = 2
                message = f'Максимальное доступное количество товара ({product.quantity}) добавлено в корзину.'
            else:
                outgoing_quantity = total_quantity_in_basket
                code = 1
                message = 'Количество товара обновлено в корзине.'
        else:
            if incoming_quantity <= product.quantity:
                outgoing_quantity = incoming_quantity
                code = 0
                message = 'Товар добавлен в корзину.'
            else:
                outgoing_quantity = product.quantity
                code = 2
                message = f'Максимальное доступное количество товара ({outgoing_quantity}) добавлено в корзину.'

        basket_data[str(product_id)] = outgoing_quantity
        redis_connection.set(guest_token, json.dumps(basket_data), ex=3600)

        response_data = {
            'code': code,
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
