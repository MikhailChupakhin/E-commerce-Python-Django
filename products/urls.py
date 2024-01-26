from django.urls import path


from products.views import (AddToComparisonView, BasketAddAnonymousView,
                            BasketAddView, BasketUpdateView, BuyInOneClickView,
                            CategoryProductsListView, ClearComparisonView,
                            CompareView, DiscountedProductsView,
                            ProductDetailView,
                            ProductSearchView, ProductsListView,
                            SubcategoryProductsListView, TagProductsListView)

app_name = 'catalog'


urlpatterns = [
    path('', ProductsListView.as_view(), name='index'),
    path('add_to_comparison/<int:product_id>/', AddToComparisonView.as_view(), name='add_to_comparison'),
    path('clear_comparison/', ClearComparisonView.as_view(), name='clear_comparison'),
    path('compare/', CompareView.as_view(), name='compare'),
    path('page/<int:page>/', ProductsListView.as_view(), name='paginator'),
    path('baskets/add/<int:product_id>/', BasketAddView.as_view(), name='basket_add'),
    path('baskets/add_anonymous/<int:product_id>/', BasketAddAnonymousView.as_view(), name='basket_add_anonymous'),
    path('baskets/update/', BasketUpdateView.as_view(), name='basket_update'),
    path('buy_in_one_click/', BuyInOneClickView.as_view(), name='buy_in_one_click'),
    path('search/', ProductSearchView.as_view(), name='product_search'),
    path('tag/<str:tag_slug>/', TagProductsListView.as_view(), name='tag_products'),
    path('discount/', DiscountedProductsView.as_view(), name='discount'),
    path('<slug:product_slug>/<int:product_id>/', ProductDetailView.as_view(), name='product_detail'),
    path('<slug:category_slug>/', CategoryProductsListView.as_view(), name='category'),
    path('<slug:category_slug>/<slug:subcategory_slug>/', SubcategoryProductsListView.as_view(), name='subcategory'),
]
