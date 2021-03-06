from django.contrib import admin
from django import forms
from gazetteer.models import *
from skosxl.models import Notation
from .settings import TARGET_NAMESPACE_FT

# Register your models here.

# works for Dango > 1.6 
class NameInline(admin.TabularInline):
    model = LocationName
    readonly_fields = ['nameUsed', 'namespace']
    extra = 0

    
class LocationTypeInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LocationTypeInlineForm, self).__init__(*args, **kwargs)
        self.fields['locationType'].queryset = Notation.objects.filter(concept__scheme__uri = TARGET_NAMESPACE_FT[0:-1] )

class LocationTypeInline(admin.StackedInline) :
    model = Notation
    form = LocationTypeInlineForm
        
class LocationAdmin(admin.ModelAdmin):
    search_fields = ['locationType__term','locationname__name']
    inlines = [
        NameInline,
    ]

class LocationNameAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_filter = ('language', 'nameUsed', 'namespace')
    
class NameFieldConfigInline(admin.TabularInline):
    model = NameFieldConfig
    extra = 1
    
class CodeFieldConfigInline(admin.TabularInline):
    model = CodeFieldConfig
    extra = 1

class LocationTypeFieldInline(admin.TabularInline):
    model = LocationTypeField

    
class GazSourceConfigAdmin(admin.ModelAdmin):
    model = GazSourceConfig
    inlines = [
        LocationTypeFieldInline, NameFieldConfigInline, CodeFieldConfigInline
    ]
    
admin.site.register(GazSource);
admin.site.register(GazSourceConfig,GazSourceConfigAdmin);
admin.site.register(Location, LocationAdmin);
admin.site.register(LocationName, LocationNameAdmin);
admin.site.register(LinkSet);
