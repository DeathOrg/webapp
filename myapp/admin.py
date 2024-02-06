# admin.py
from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'account_created', 'account_updated']
    search_fields = ['username', 'first_name', 'last_name']
    readonly_fields = ['account_created', 'account_updated']

    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'password'),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # If this is a new object being created
            obj.set_password(form.cleaned_data['password'])  # Set password using set_password method
        super().save_model(request, obj, form, change)