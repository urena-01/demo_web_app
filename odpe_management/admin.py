from django.contrib import admin

# Register your models here.
from .models import *

admin.site.site_header = "TROOP Admin"
admin.site.site_title = "TROOP Admin Portal"
admin.site.index_title = "Welcome to TROOP Portal"


@admin.register(Employee)
class AdminEmployee(admin.ModelAdmin):
    list_display = (
        'rank', 'contact', 'status', 'address', 'city', 'state', 'type',)
    list_per_page = 10
    list_filter = ('rank', 'contact', 'status', 'address', 'city', 'state', 'type',)
    search_fields = ('rank', 'contact', 'address', 'type',)


@admin.register(Company)
class AdminCompany(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_per_page = 10
    list_filter = ('id', 'name',)
    search_fields = ('id', 'name',)


@admin.register(Job)
class AdminJob(admin.ModelAdmin):
    list_display = (
        'id', 'performed_by', 'company', 'start_date', 'end_date', 'hours', 'post', 'pay', 'pay_status',
        'invoice')
    list_per_page = 10
    list_filter = (
        'id', 'performed_by', 'company', 'start_date', 'end_date', 'hours', 'post', 'pay', 'pay_status',
        'invoice',
    )
    search_fields = (
        'id', 'performed_by', 'company', 'start_date', 'end_date', 'hours', 'post', 'pay', 'pay_status',
        'invoice',
    )


@admin.register(JobType)
class AdminJobType(admin.ModelAdmin):
    list_display = ('id', 'company', 'name')
    list_per_page = 10
    list_filter = ('id', 'company', 'name',)
    search_fields = ('id', 'company', 'name',)


@admin.register(Rank)
class AdminRank(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_per_page = 10
    list_filter = ('id', 'name',)
    search_fields = ('id', 'name',)


@admin.register(Agency)
class AdminAgency(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_per_page = 10
    list_filter = ('id', 'name',)
    search_fields = ('id', 'name',)


@admin.register(Troop)
class AdminTroop(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_per_page = 10
    list_filter = ('id', 'name',)
    search_fields = ('id', 'name',)
