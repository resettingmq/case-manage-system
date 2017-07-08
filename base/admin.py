from django.contrib import admin
from . import models
# Register your models here.


class CountryInline(admin.StackedInline):
    model = models.Country
    extra = 3


class ContinentAdmin(admin.ModelAdmin):
    inlines = [CountryInline]

admin.site.register(models.Continent, ContinentAdmin)
admin.site.register(models.Country)
