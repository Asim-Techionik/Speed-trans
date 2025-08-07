# admin.py
from django.contrib import admin
from .models import CustomUser, Load
#Dispatcher, Driver.


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_type', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    list_filter = ('user_type', 'is_staff', 'is_superuser')

    # Allow admin to create users
    def save_model(self, request, obj, form, change):
        if not change:
            obj.set_password(obj.password)  # Ensure password is hashed
        super().save_model(request, obj, form, change)


@admin.register(Load)
class LoadAdmin(admin.ModelAdmin):
    list_display = ('loadname', 'pickup_location', 'delivery_location', 'pickup_date', 'delivery_date', 'status')
    search_fields = ('loadname', 'pickup_location', 'delivery_location')
    list_filter = ('status',)


# @admin.register(Dispatcher)
# class DispatcherAdmin(admin.ModelAdmin):
#     list_display = ('first_name', 'last_name', 'email', 'username', 'location_branch')
#     search_fields = ('first_name', 'last_name', 'email', 'username')
#     list_filter = ('gender', 'location_branch')
#
#
# @admin.register(Driver)
# class DriverAdmin(admin.ModelAdmin):
#     list_display = ('first_name', 'last_name', 'email', 'license_number', 'vehicle_type', 'vehicle_plate_no')
#     search_fields = ('first_name', 'last_name', 'email', 'license_number')
#     list_filter = ('vehicle_type',)