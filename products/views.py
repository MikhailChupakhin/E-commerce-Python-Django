import json
import logging
from statistics import mean

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q, Count, Exists, OuterRef
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.db import transaction

from common.views import TitleMixin
from orders.models import BuyInOneClick
from products.models import (Basket, ComparisonList, FeaturedProducts,
                             Manufacturer, Product,
                             ProductCategory, ProductSubCategory, FeaturedSubcategory)
from reviews.models import ProductReview
from seo_manager.models import SliderImage, InfoPage


logger = logging.getLogger('main')


def apply_filters_and_sort(queryset, request):
    sort_param = request.GET.get('sort')
    if sort_param == 'name':
        queryset = queryset.order_by('name')
    elif sort_param == '-name':
        queryset = queryset.order_by('-name')
    elif sort_param == 'by_price':
        queryset = queryset.order_by('price')
    elif sort_param == '-by_price':
        queryset = queryset.order_by('-price')
    elif not sort_param:
        queryset = queryset.order_by('id')

    min_price = request.GET.get('min_price_value')
    max_price = request.GET.get('max_price_value')
    in_stock = request.GET.get('in_stock')
    manufacturers = request.GET.getlist('manufacturer[]')

    if min_price:
        try:
            min_price = float(min_price)
            queryset = queryset.filter(price__gte=min_price)
        except (ValueError, ValidationError):
            pass

    if max_price:
        try:
            max_price = float(max_price)
            queryset = queryset.filter(price__lte=max_price)
        except (ValueError, ValidationError):
            pass

    if in_stock:
        queryset = queryset.filter(quantity__gt=0)

    if manufacturers:
        manufacturer_names = queryset.filter(manufacturer__name__in=manufacturers).values_list('manufacturer__name', flat=True).distinct()
        queryset = queryset.filter(manufacturer__name__in=manufacturer_names)

    return queryset


class BaseView(View):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['company_info'] = InfoPage.objects.filter(section=1).values('title', 'slug')
        context['clients_info'] = InfoPage.objects.filter(section=2).values('title', 'slug')

        if self.request.user.is_authenticated:
            basket_items = Basket.objects.filter(user=self.request.user)
            total_items = sum(item.quantity for item in basket_items)
            context['products_in_cart'] = total_items
        else:
            basket_items = self.request.session.get('basket', {})
            context['products_in_cart'] = len(basket_items)

        return context

    def get_sort_order(self):
        sort_param = self.request.GET.get('sort')
        if sort_param in ['name', '-name', 'price', '-price']:
            return sort_param
        else:
            return 'id'


class IndexView(BaseView, TitleMixin, TemplateView):
    template_name = 'products/index.html'

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        active_sliders = SliderImage.objects.filter(is_active=True)
        context['active_sliders'] = active_sliders

        featured_products = FeaturedProducts.objects.first()
        context['featured_products'] = featured_products.products.all()
        return self.render_to_response(context)


class ProductsListView(BaseView, TitleMixin, ListView):
    model = Product
    template_name = 'products/products.html'
    paginate_by = 9
    page_title = 'Каталог'

    def create_session_if_not_exists(self):
        if not self.request.session.session_key:
            self.request.session.save()

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = apply_filters_and_sort(queryset, self.request)
        return queryset

    def get_context_data(self, **kwargs):
        self.create_session_if_not_exists()
        context = super().get_context_data(**kwargs)

        session_id = self.request.session.session_key
        context['session_id'] = session_id
        context['page_title'] = self.page_title

        comparison_list = None
        try:
            comparison_list = ComparisonList.objects.get(session=session_id)
        except:
            pass

        if comparison_list:
            comparison_products = comparison_list.products.all()

            comparison_product_ids = list(comparison_products.values_list('id', flat=True))
            context['comparison_product_ids'] = comparison_product_ids

        categories_cache_key = 'categories_list'
        categories = cache.get(categories_cache_key)
        if categories is None:
            categories = list(ProductCategory.objects.all())
            cache.set(categories_cache_key, categories, 3600)
        context['categories'] = categories

        manufacturers_cache_key = 'manufacturers_list'
        manufacturers = cache.get(manufacturers_cache_key)

        if manufacturers is None:
            manufacturers = (
                Manufacturer.objects
                .annotate(has_products=Exists(Product.objects.filter(manufacturer=OuterRef('pk'))))
                .filter(has_products=True)
                .order_by('name')
                .all()
            )
            cache.set(manufacturers_cache_key, manufacturers, 3600)

        context['manufacturers'] = manufacturers

        queryset = self.get_queryset()
        queryset = queryset.prefetch_related('characteristics')
        products_count = queryset.count()
        context['products_count'] = products_count
        context['product_list'] = queryset

        featured_subcategories = FeaturedSubcategory.objects.all()
        context['featured_subcategories'] = featured_subcategories

        context['min_price'] = self.request.GET.get('min_price_value')
        context['max_price'] = self.request.GET.get('max_price_value')
        context['in_stock'] = self.request.GET.get('in_stock')
        context['manufacturers_filter'] = self.request.GET.getlist('manufacturer[]')


        context['sort'] = self.request.GET.get('sort')

        return context


class CategoryProductsListView(ProductsListView):
    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.kwargs.get('category_slug')
        category = get_object_or_404(ProductCategory, slug=category_slug)

        queryset = queryset.filter(category=category)
        queryset = apply_filters_and_sort(queryset, self.request)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        category_slug = self.kwargs.get('category_slug')
        category = get_object_or_404(ProductCategory, slug=category_slug)

        context['page_title'] = category.name
        context['category_slug'] = category_slug

        context['category'] = category

        page_number = self.request.GET.get('page')
        paginator = Paginator(context['product_list'], self.paginate_by)
        page_obj = paginator.get_page(page_number)
        context['product_list'] = page_obj
        context['sort'] = self.request.GET.get('sort')

        return context


class SubcategoryProductsListView(ProductsListView):
    def get_queryset(self):
        queryset = super().get_queryset()
        subcategory_slug = self.kwargs.get('subcategory_slug')
        sub_category = get_object_or_404(ProductSubCategory, slug=subcategory_slug)

        queryset = queryset.filter(sub_category=sub_category)
        queryset = apply_filters_and_sort(queryset, self.request)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('category_slug')
        subcategory_slug = self.kwargs.get('subcategory_slug')
        sub_category = get_object_or_404(ProductSubCategory, slug=subcategory_slug)

        context['category_slug'] = category_slug
        context['subcategory_slug'] = subcategory_slug
        context['subcategory'] = sub_category
        context['page_title'] = sub_category.name
        context['sort'] = self.request.GET.get('sort')
        return context


class TagProductsListView(ListView):
    model = Product
    template_name = 'products/products.html'
    context_object_name = 'products'

    def get_queryset(self):
        tag_slug = self.kwargs['tag_slug']
        cache_key = f'tag_products_{tag_slug}_queryset'
        queryset = cache.get(cache_key)
        if queryset is None:
            queryset = Product.objects.filter(tags__slug=tag_slug)
            cache.set(cache_key, queryset, 3600)

        return queryset


class ProductSearchView(ProductsListView):
    template_name = 'products/products.html'
    paginate_by = 9
    context_object_name = 'products'

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['keyword'] = self.request.GET.get('keyword')

        return context


class DiscountedProductsView(ProductsListView):
    template_name = 'products/products.html'
    context_object_name = 'products'

    def get_queryset(self):
        cache_key = "discounted_products"

        cached_queryset = cache.get(cache_key)

        if cached_queryset is None:
            products = Product.objects.filter(discount_percentage__gt=0)
            cached_queryset = products
            cache.set(cache_key, cached_queryset, 3600)

        return cached_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ProductDetailView(BaseView, TitleMixin, DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    title = 'IMSOUND - '

    def get_object(self, queryset=None):
        product_id = self.kwargs.get('product_id')

        # category = get_object_or_404(ProductCategory, slug=category_slug)
        # subcategory = get_object_or_404(ProductSubCategory, slug=subcategory_slug)

        queryset = self.get_queryset()
        product = get_object_or_404(queryset, id=product_id)

        return product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['category'] = self.object.category
        context['title'] += self.object.name

        categories_cache_key = 'categories_list'
        categories = cache.get(categories_cache_key)
        if categories is None:
            categories = list(ProductCategory.objects.all())
            cache.set(categories_cache_key, categories, 3600)
        context['categories'] = categories

        context['product_characteristics'] = {characteristic.name: characteristic.value for characteristic in
                                              self.object.characteristics.all()}

        reviews = ProductReview.objects.filter(product=self.object, moderated=True)
        context['reviews'] = reviews
        average_rating = mean(review.rating for review in reviews) if reviews else None
        context['average_rating'] = average_rating

        viewed_product_ids = self.request.session.get('viewed_products', [])
        current_product_id = self.object.id

        if current_product_id not in viewed_product_ids:
            viewed_product_ids.append(current_product_id)
            self.request.session['viewed_products'] = viewed_product_ids

        context['viewed_products'] = Product.objects.filter(id__in=viewed_product_ids).exclude(id=self.object.id)[:10]

        similar_products = Product.objects.filter(sub_category=self.object.sub_category).exclude(
            id__in=viewed_product_ids).exclude(id=self.object.id)[:10]
        context['similar_products'] = similar_products

        # !!! Определиться с механизмами персональных рекомендаций
        recommended_products = Product.objects.exclude(id__in=viewed_product_ids).exclude(
            id__in=similar_products.values_list('id', flat=True))[:10]
        context['recommended_products'] = recommended_products
        return context


class BuyInOneClickView(View):
    def post(self, request):
        post_data = json.loads(request.body.decode("utf-8"))
        try:
            name = post_data.get('name')
            phone = post_data.get('phone')
            email = post_data.get('email')
            product_id = post_data.get('product_id')

            product = Product.objects.get(pk=product_id)
            BuyInOneClick.objects.create(name=name, phone=phone, email=email, product=product)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.error("Error:", str(e))
            return JsonResponse({'status': 'error', 'message': str(e)})


class BasketAddView(LoginRequiredMixin, View):
    @transaction.atomic
    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            logger.error(f'Продукт не был найден, ID:{product_id}, USER: {request.user.id}')
            return JsonResponse({'error': 'Продукт не найден.'}, status=404)

        post_data = json.loads(request.body.decode("utf-8"))
        quantity = int(post_data.get('quantity', 1))

        if quantity < 1:
                return JsonResponse({'error': 'Некорректное количество товара.'}, status=400)

        try:
            basket = Basket.objects.get(user=request.user, product=product)
            total_quantity_in_basket = basket.quantity + quantity
            if total_quantity_in_basket > product.quantity:
                quantity = max(0, product.quantity - basket.quantity)
                message = 'Доступное количество товара уже добавлено в корзину.'
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

        basket_items = Basket.objects.filter(user=request.user)
        return JsonResponse(response_data)


class BasketAddAnonymousView(View):
    def post(self, request, product_id):
        product = Product.objects.get(id=product_id)
        post_data = json.loads(request.body.decode("utf-8"))
        quantity = int(post_data.get('quantity', 1))

        basket = request.session.get('basket', {})

        if product.quantity == 0:
            return JsonResponse({'message': 'Invalid quantity'}, status=200)

        basket_item = basket.get(str(product_id))

        if basket_item:
            total_quantity_in_basket = basket_item['quantity'] + quantity
            if total_quantity_in_basket > product.quantity:
                basket_item['quantity'] = product.quantity
                message = 'The maximum available quantity has already been added to the basket.'
            else:
                basket_item['quantity'] = total_quantity_in_basket
                message = 'Product quantity updated in the basket.'
        else:
            if quantity > product.quantity:
                quantity = product.quantity
            basket[str(product_id)] = {'quantity': quantity}
            message = 'Product added to the basket.'

        request.session['basket'] = basket

        response_data = {
            'message': message,
            'available_quantity': product.quantity,
            'added_quantity': quantity,
        }

        return JsonResponse(response_data)


class BasketUpdateView(View):
    def post(self, request):
        removed_items = request.POST.getlist('removed_items[]')
        quantity_items = {}

        for key, value in request.POST.items():
            if key.startswith('quantity_'):
                item_id = key.split('_')[1]
                quantity_items[item_id] = int(value)

        for item_id, quantity in quantity_items.items():
            basket = Basket.objects.get(id=item_id)
            basket.quantity = quantity
            basket.save()

        Basket.objects.filter(id__in=removed_items).delete()

        message = 'Basket was updated.'

        response_data = {
            'message': message,
        }
        return JsonResponse(response_data)


class AddToComparisonView(View):
    def post(self, request, product_id):
        post_data = json.loads(request.body.decode("utf-8"))
        session_id = post_data.get('session_id')
        product = Product.objects.get(id=post_data.get('product_id'))

        try:
            comparison_list = ComparisonList.objects.get(session_id=session_id)
        except ComparisonList.DoesNotExist:
            comparison_list = ComparisonList.objects.create(session_id=session_id)

        if product in comparison_list.products.all():
            comparison_list.products.remove(product)
            return JsonResponse({'message': 'Товар удален из списка для сравнения', 'product_count': comparison_list.products.count()}, status=200)

        if comparison_list.products.count() == 3:
            return JsonResponse({'message': 'Превышено максимальное количество товаров для сравнения', 'product_count': comparison_list.products.count()}, status=400)

        comparison_list.products.add(product)
        return JsonResponse({'message': 'Товар добавлен для сравнения', 'product_count': comparison_list.products.count()}, status=200)


class ClearComparisonView(View):
    def post(self, request, *args, **kwargs):
        session_id = request.session.session_key
        try:
            comparison_list = ComparisonList.objects.get(session_id=session_id)
        except ComparisonList.DoesNotExist:
            pass
        if comparison_list:
            comparison_list.delete()
        response_data = {'message': 'Список сравнения успешно очищен.'}
        return JsonResponse(response_data)


class CompareView(View):
    def get(self, request):
        session_id = request.session.session_key
        try:
            comparison_list = ComparisonList.objects.get(session_id=session_id)
            products = comparison_list.products.all()

            total_characteristics = []
            for product in products:
                characteristics = product.characteristics.all()
                for characteristic in characteristics:
                    characteristic_name = characteristic.name
                    if characteristic_name not in total_characteristics:
                        total_characteristics.append(characteristic_name)

            context = {
                'products': products,
                'total_characteristics': total_characteristics,
            }

        except ComparisonList.DoesNotExist:
            context = {
                'products': [],
                'total_characteristics': [],
            }

        return render(request, 'products/compare.html', context)

