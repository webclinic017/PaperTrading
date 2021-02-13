from django.contrib import admin
from appUsers.models import CustomUser
from django.contrib.auth.admin import UserAdmin


class AccountAdmin(UserAdmin):

    # fields that show up in admins page when user details are displayed
    list_display = ('email', 'username', 'date_joined', "api_key" , 'last_login', 'is_admin', 'is_staff', 'is_superuser')

    # fields that search is carried out on in admin page
    search_fields = ('email', 'username')

    # fields that cannot be edited
    readonly_fields = ('id', 'date_joined', 'last_login')

    filter_horizontal = ()

    # filter option in admin page
    list_filter = ('is_admin', 'is_staff', 'is_superuser')
    fieldsets = ()

    # define the fields that will be displayed on the create user page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'broker', 'api_key', 'secret_key',
                       'is_admin', 'is_active', 'is_staff', 'is_superuser')}),)


# This line of code appends CustomUser model to admin site and applies AccountAdmin view to it.
admin.site.register(CustomUser, AccountAdmin)

