import json
import logging
from statistics import mean

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.db import transaction

from common.views import TitleMixin
from orders.models import BuyInOneClick
from orders.tasks import send_notification_on_create
from products.models import (Basket, ComparisonList, FeaturedProducts,
                             Manufacturer, Product,
                             ProductCategory, ProductSubCategory)
from reviews.models import ProductReview
from seo_manager.models import SliderImage, InfoPage

logger = logging.getLogger('main')


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

    def get_queryset(self):
        queryset = super().get_queryset()
        sort_param = self.request.GET.get('sort')

        cache_key = f"product_list_{sort_param}"
        cached_queryset = cache.get(cache_key)
        if cached_queryset is None:
            cached_queryset = super().get_queryset()

            if sort_param == 'name':
                cached_queryset = queryset.order_by('name')
            elif sort_param == '-name':
                cached_queryset = queryset.order_by('-name')
            elif sort_param == 'by_price':
                cached_queryset = queryset.order_by('price')
            elif sort_param == '-by_price':
                cached_queryset = queryset.order_by('-price')

            cache.set(cache_key, cached_queryset, 3600)

        return cached_queryset

    def create_session_if_not_exists(self):
        if not self.request.session.session_key:
            self.request.session.save()

    def get_context_data(self, **kwargs):
        self.create_session_if_not_exists()
        context = super().get_context_data(**kwargs)

        session_id = self.request.session.session_key
        context['session_id'] = session_id
        context['page_title'] = self.page_title

        comparison_list = None  # Инициализация переменной
        try:
            comparison_list = ComparisonList.objects.get(session=session_id)
        except:
            pass

        if comparison_list:
            comparison_products = comparison_list.products.all()

            # Получаем список идентификаторов товаров из comparison_products
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
            manufacturers = list(Manufacturer.objects.all())
            cache.set(manufacturers_cache_key, manufacturers, 3600)
        context['manufacturers'] = manufacturers

        queryset = self.get_queryset()
        # Получение характеристик для каждого товара с использованием prefetch_related
        queryset = queryset.prefetch_related('characteristics')
        products_count = queryset.count()
        context['products_count'] = products_count
        context['product_list'] = queryset

        return context


class CategoryProductsListView(ProductsListView):

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.kwargs.get('category_slug')
        category = get_object_or_404(ProductCategory, slug=category_slug)

        sort_param = self.request.GET.get('sort')
        cache_key = f"product_list_{sort_param}_{category_slug}"

        cached_queryset = cache.get(cache_key)

        if cached_queryset is None:
            cached_queryset = queryset.filter(category=category)

            if sort_param == 'name':
                cached_queryset = queryset.order_by('name')
            elif sort_param == '-name':
                cached_queryset = queryset.order_by('-name')
            elif sort_param == 'by_price':
                cached_queryset = queryset.order_by('price')
            elif sort_param == '-by_price':
                cached_queryset = queryset.order_by('-price')

            cache.set(cache_key, cached_queryset, 3600)

        return cached_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        category_slug = self.kwargs.get('category_slug')
        category = get_object_or_404(ProductCategory, slug=category_slug)

        context['page_title'] = category.name  # Здесь получаем имя из объекта category
        context['category_slug'] = category_slug

        context['category'] = category

        page_number = self.request.GET.get('page')
        paginator = Paginator(context['product_list'], self.paginate_by)
        page_obj = paginator.get_page(page_number)
        context['product_list'] = page_obj

        return context


class SubcategoryProductsListView(ProductsListView):
    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.kwargs.get('category_slug')
        subcategory_slug = self.kwargs.get('subcategory_slug')
        sub_category = get_object_or_404(ProductSubCategory, slug=subcategory_slug)
        sort_param = self.request.GET.get('sort')

        cache_key = f"subcategory_product_list_{category_slug}_{subcategory_slug}_{sort_param}"

        cached_queryset = cache.get(cache_key)

        if cached_queryset is None:
            cached_queryset = queryset.filter(sub_category=sub_category)

            if sort_param == 'name':
                cached_queryset = queryset.order_by('name')
            elif sort_param == '-name':
                cached_queryset = queryset.order_by('-name')
            elif sort_param == 'by_price':
                cached_queryset = queryset.order_by('price')
            elif sort_param == '-by_price':
                cached_queryset = queryset.order_by('-price')

            cache.set(cache_key, cached_queryset, 3600)

        return cached_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('category_slug')
        subcategory_slug = self.kwargs.get('subcategory_slug')
        sub_category = get_object_or_404(ProductSubCategory, slug=subcategory_slug)

        context['category_slug'] = category_slug
        context['subcategory_slug'] = subcategory_slug
        context['subcategory'] = sub_category
        context['page_title'] = sub_category.name  # Здесь получаем имя из объекта sub_category
        return context


class ProductFilterView(ProductsListView):

    def get_queryset(self):
        if hasattr(self, 'filtered_queryset'):
            return self.filtered_queryset

        queryset = Product.objects.all()
        # Получение параметров фильтрации из запроса
        min_price = self.request.GET.get('min_price_value')
        max_price = self.request.GET.get('max_price_value')
        in_stock = self.request.GET.get('in_stock')
        manufacturers = self.request.GET.getlist('manufacturer[]')
        print(manufacturers)
        # Применение фильтров по цене
        if min_price:
            try:
                min_price = float(min_price)
                queryset = queryset.filter(price__gte=min_price)
                print(f"Длина QuerySet min-price: {len(queryset)}")
            except (ValueError, ValidationError):
                # Обработка неправильного значения для min_price
                pass

        if max_price:
            try:
                max_price = float(max_price)
                queryset = queryset.filter(price__lte=max_price)
                print(f"Длина QuerySet max-price: {len(queryset)}")
            except (ValueError, ValidationError):
                # Обработка неправильного значения для max_price
                pass

        # Применение фильтра "В наличии"
        if in_stock:
            print(f"Длина QuerySet in_stock: {len(queryset)}")
            queryset = queryset.filter(quantity__gt=0)

        # Применение фильтра "По производителю"
        if manufacturers:
            manufacturer_names = queryset.filter(manufacturer__name__in=manufacturers).values_list('manufacturer__name',
                                                                                                   flat=True).distinct()

            # Выведите список уникальных значений
            print("Производители, с которыми выполняется сравнение:")
            for name in manufacturer_names:
                print(name)
            print(f"Длина QuerySet manufacturers-до: {len(queryset)}")
            queryset = queryset.filter(manufacturer__name__icontains=manufacturer_names)
            print(f"Длина QuerySet manufacturers-после: {len(queryset)}")

        # Применяем сортировку к queryset
        sort_param = self.request.GET.get('sort')
        if sort_param == 'name':
            queryset = queryset.order_by('name')
        elif sort_param == '-name':
            queryset = queryset.order_by('-name')
        elif sort_param == 'by_price':
            queryset = queryset.order_by('price')
        elif sort_param == '-by_price':
            queryset = queryset.order_by('-price')

        # Применяем prefetch_related к queryset
        queryset = queryset.prefetch_related('characteristics')

        # Сохраняем фильтрованный QuerySet в атрибуте объекта представления
        self.filtered_queryset = queryset

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Добавление параметров фильтрации в контекст
        context['min_price'] = self.request.GET.get('min_price_value')
        context['max_price'] = self.request.GET.get('max_price_value')
        context['manufacturer'] = self.request.GET.getlist('manufacturer[]')
        context['in_stock'] = self.request.GET.get('in_stock')

        # Используем Paginator для разбиения queryset на страницы
        paginator = Paginator(self.get_queryset(), per_page=9)
        page_number = self.request.GET.get('page')
        page = paginator.get_page(page_number)

        context['object_list'] = page

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
            # Формируем уникальный ключ
            cache_key = f"product_search_{keyword}"

            # Попытка получить результаты из кэша
            cached_queryset = cache.get(cache_key)

            if cached_queryset is None:
                print('CACHE NONE')
                # Если результаты не найдены в кэше, выполняем фильтрацию и кэшируем результат
                products = Product.objects.filter(
                    Q(name__icontains=keyword) |
                    Q(category__name__icontains=keyword) |
                    Q(sub_category__name__icontains=keyword)
                ).order_by('name').prefetch_related('characteristics')
                cached_queryset = products
                cache.set(cache_key, cached_queryset, 3600)  # Кэшируем на час

            return cached_queryset
        else:
            return Product.objects.none()  # Возвращаем пустой QuerySet, чтобы избежать ошибки

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['keyword'] = self.request.GET.get('keyword')

        return context


class DiscountedProductsView(ProductsListView):
    template_name = 'products/products.html'
    context_object_name = 'products'

    def get_queryset(self):
        cache_key = "discounted_products"

        # Попытка получить результаты из кэша
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
        product_slug = self.kwargs.get('product_slug')
        category_slug = self.kwargs.get('category_slug')
        subcategory_slug = self.kwargs.get('subcategory_slug')

        # Получаем объекты Категории и Подкатегории на основе их слагов
        category = get_object_or_404(ProductCategory, slug=category_slug)
        subcategory = get_object_or_404(ProductSubCategory, slug=subcategory_slug)

        # Получаем объект продукта, связанный с указанной Категорией и Подкатегорией
        queryset = self.get_queryset()
        product = get_object_or_404(queryset, slug=product_slug, category=category, sub_category=subcategory)

        return product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Основные данные о товаре и категории
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

        # Получаем отзывы для данного продукта, где moderated=True
        reviews = ProductReview.objects.filter(product=self.object, moderated=True)
        context['reviews'] = reviews
        # Расчет среднего рейтинга
        average_rating = mean(review.rating for review in reviews) if reviews else None
        context['average_rating'] = average_rating

        # Получаем список идентификаторов просмотренных товаров из сессии или инициализируем его
        viewed_product_ids = self.request.session.get('viewed_products', [])
        current_product_id = self.object.id

        # Добавляем идентификатор текущего товара в список просмотренных, если его там еще нет
        if current_product_id not in viewed_product_ids:
            viewed_product_ids.append(current_product_id)
            # Сохраняем обновленный список просмотренных товаров обратно в сессию
            self.request.session['viewed_products'] = viewed_product_ids

        # Контекст блока "Просмотренные товары"
        context['viewed_products'] = Product.objects.filter(id__in=viewed_product_ids).exclude(id=self.object.id)[:10]

        # Контекст блока "Похожие товары"
        similar_products = Product.objects.filter(sub_category=self.object.sub_category).exclude(
            id__in=viewed_product_ids).exclude(id=self.object.id)[:10]
        context['similar_products'] = similar_products

        # Контекст блока "Рекомендованные товары"
        # Исключаем идентификаторы просмотренных и похожих товаров из запроса данных для рекомендованных товаров
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


@receiver(post_save, sender=BuyInOneClick)
def send_buyinoneclick_notification(sender, instance, created, **kwargs):
    if created:
        message_text = f"Заказ в 1 клик! ID: {instance.id} Дата: {instance.created.strftime('%Y-%m-%d %H:%M')} Email: {instance.email}"
        send_notification_on_create.apply_async(args=[message_text])


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

        # Проверяем, если товар уже есть в корзине
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

        # Получение данных корзины из сессии
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

        # Получение измененных значений количества товаров из параметров запроса
        for key, value in request.POST.items():
            if key.startswith('quantity_'):
                item_id = key.split('_')[1]
                quantity_items[item_id] = int(value)

        # Обновление количества товаров в корзине
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

