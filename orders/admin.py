from django.contrib import admin
from .models import Order,Payment,OrderProduct


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = [
        'payment',
        'user',
        'product',
        'quantity',
        'product_price',
        'ordered',
    
    ]
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = [ 
    'order_number',
    'full_name',
    'phone',
    'email',
    'city',
    'order_total',
    'shipping_cost',
    'status',
    'is_ordered',
    'created_at',
    ]
    list_filter = [    'status',
    'is_ordered']
    search_fields = [
    'order_number',
    'first_name',
    'email',
    'status',
    ]
    list_per_page = 20
    inlines = [OrderProductInline]

admin.site.register(Order,OrderAdmin)
admin.site.register(Payment)
admin.site.register(OrderProduct)