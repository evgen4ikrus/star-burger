from django.contrib import admin
from django.shortcuts import reverse
from django.templatetags.static import static
from django.utils.html import format_html

from .models import (Customer, Order, Product, ProductCategory, Restaurant,
                     RestaurantMenuItem)


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url)
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html(
            '<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>',
            edit_url=edit_url, src=obj.image.url)
    get_image_list_preview.short_description = 'превью'


class OrderInline(admin.TabularInline):
    model = Order
    fields = ('product', 'price', 'quantity', 'get_total_price')
    readonly_fields = ['get_total_price']

    def get_total_price(self, obj):
        price, quantity = obj.price, obj.quantity
        if price and quantity:
            return price * quantity
        return '-'

    get_total_price.short_description = 'Общая цена'


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    inlines = [
        OrderInline,
    ]

    class Meta:
        managed = True
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    pass
