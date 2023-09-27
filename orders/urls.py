from django.urls import path
from . import views


urlpatterns = [
    path('place_order/', views.Place_Order, name='place_order'),
    path('payments/', views.Payments, name='payments'),
    path('order_complete/', views.Order_Complete, name='order_complete'),

]