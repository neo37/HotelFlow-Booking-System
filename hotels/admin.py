from django.contrib import admin
from .models import Hotel, HotelImage, Room, Booking


class HotelImageInline(admin.TabularInline):
    model = HotelImage
    extra = 1
    fields = ['image', 'caption', 'order']


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'created_at']
    search_fields = ['name', 'address']
    inlines = [HotelImageInline]


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'hotel', 'area', 'price_per_night']
    list_filter = ['hotel']
    search_fields = ['name', 'hotel__name']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['room', 'guest_name', 'check_in', 'check_out', 'status']
    list_filter = ['status', 'check_in', 'check_out']
    search_fields = ['guest_name', 'guest_email', 'room__name']

