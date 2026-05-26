from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import NewUser


@admin.register(NewUser)
class NewUserAdmin(UserAdmin):

    model = NewUser

    ordering = ('email',)

    list_display = (
        'email',
        'user_name',
        'first_name',
        'last_name',
        'role',
        'is_staff',
        'is_active',
    )

    search_fields = (
        'email',
        'user_name',
        'first_name',
        'last_name',
    )

    fieldsets = (
        (None, {
            'fields': (
                'email',
                'password',
            )
        }),

        ('Personal Info', {
            'fields': (
                'user_name',
                'first_name',
                'last_name',
                'bio_pitcure',
                'organization',
            )
        }),

        ('Role & Status', {
            'fields': (
                'role',
                'is_active',
                'is_verified',
                'is_password_temp',
                'created_organization',
                'is_staff',
                'is_superuser',
            )
        }),

        ('Permissions', {
            'fields': (
                'groups',
                'user_permissions',
            )
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'user_name',
                'first_name',
                'last_name',
                'password1',
                'password2',
                'is_staff',
                'is_active',
            ),
        }),
    )