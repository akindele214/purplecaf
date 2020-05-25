from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import (products, AddItemView, ItemDetailView, 
                    EditItemView, remove_from_cart, remove_single_item_from_cart, 
                    add_single_item_from_cart, add_to_cart, add_to_cart_json, CategoryListView, delete_from_cart,
                    OrderSummaryView, HomeView, CheckOutView, CashPaymentView, ProfileSummaryView,
                    OrderListView, OrderDetailView, CardPaymentView,
                    ProcessPaymentView, CardPaymentCancelView, CardPaymentSucessView, SearchView
                    , AddVoucher, ViewVoucherAccount, SearchVoucher, VoucherPaymentView, ViewVoucherAccount)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('checkout/', CheckOutView.as_view(), name='checkout'),
    path('search/', SearchView.as_view(), name='search'),
    path('search-v/', SearchVoucher.as_view(), name="search-voucher"),
    path('loadvoucher/<str:username>', AddVoucher.as_view(), name='load-voucher'),
    # path('voucher/', ViewVoucherAccount.as_view(), name='voucher-account'),
    path('view-voucher/', ViewVoucherAccount.as_view(), name='voucher-account'),
    path('add-item/', AddItemView.as_view(), name='add-item'),
    path('item-detail/<slug>/', ItemDetailView.as_view(), name="product"),
    path('edit-item/<slug>/', EditItemView.as_view(), name="edit-item"),
    path('category/<cat>/', CategoryListView.as_view(), name='category'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),    
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('delete-from-cart/<slug>/', delete_from_cart, name='delete-from-cart'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('json-add-to-cart/<slug>/', add_to_cart_json, name='json-add-to-cart'),
    path('add-single-item-to-cart/<slug>/', add_single_item_from_cart, name="add-single-item-to-cart"),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart, name='remove-single-item-from-cart'),   
    path('voucher-payment/', VoucherPaymentView.as_view(), name="voucher-payment"),
    path('card-payment/', CardPaymentView.as_view(), name='card-payment'),
    path('profile/', ProfileSummaryView.as_view(), name='profile'),
    path('orders', OrderListView.as_view(), name="orders"),
    path('order/<ref>/', OrderDetailView.as_view(), name="order-detail"),     
    path('processpayment/', ProcessPaymentView.as_view(), name='process-payment'),
    path('paymentsuccess/', CardPaymentSucessView.as_view(), name='success-payment'),
    path('cancelpayment/', CardPaymentCancelView.as_view(), name='cancel-payment')
]