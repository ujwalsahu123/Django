from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Pizza, Cart, CartItem, Order, OrderItem

@admin.register(Pizza)
class PizzaAdmin(admin.ModelAdmin):
    list_display = ('name', 'size', 'price', 'is_available', 'display_image', 'toppings')
    list_filter = ('is_available', 'size')
    search_fields = ('name', 'description', 'toppings')
    list_editable = ('price', 'is_available')
    readonly_fields = ('display_image',)
    
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', obj.image.url)
        return "No image"
    display_image.short_description = 'Preview'

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('subtotal',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'total', 'item_count')
    inlines = [CartItemInline]
    
    def item_count(self, obj):
        return obj.cartitem_set.count()
    item_count.short_description = 'Number of Items'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price', 'subtotal')
    
    def subtotal(self, obj):
        return obj.price * obj.quantity if obj.price and obj.quantity else 0
    subtotal.short_description = 'Subtotal'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_info', 'status', 'created_at', 'total_amount', 'phone_number')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'delivery_address', 'phone_number')
    inlines = [OrderItemInline]
    readonly_fields = ('total_amount', 'created_at', 'updated_at')
    list_editable = ('status',)
    
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'status', 'total_amount')
        }),
        ('Delivery Information', {
            'fields': ('delivery_address', 'phone_number')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def user_info(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_info.short_description = 'Customer'

# Customize admin site
admin.site.site_header = 'Pizza Shop Administration'
admin.site.site_title = 'Pizza Shop Admin'
admin.site.index_title = 'Pizza Shop Management'
