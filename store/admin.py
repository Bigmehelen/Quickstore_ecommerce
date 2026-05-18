from django.contrib import admin
from .models import Product, Order, Collection, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title','price','updated_at','inventory']
    list_per_page = 10
    search_fields = ['title','description']
    list_editable = ['price','inventory']
    inlines = [ProductImageInline]


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['id','title']
