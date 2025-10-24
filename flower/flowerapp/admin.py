from django.contrib import admin

# Register your models here.
from django.contrib import admin
import logging
from .forms import CustomTimeSeriesPlotPointImportForm,CustomConfirmTimeSeriesPlotPointImportForm
from .models import Track
from .models import Item
from .models import TimeSeriesPlotPoint
from import_export.fields import Field
from import_export.resources import ModelResource
from import_export.admin import ImportMixin
import random

# Customize Django Admin site titles
admin.site.site_header = 'Timeflower Administration'
admin.site.site_title = 'Timeflower Admin'
admin.site.index_title = 'Welcome to Timeflower Administration'

# Simple solution: Override admin index redirect
from django.conf import settings
from django.shortcuts import redirect
from django.http import HttpResponseRedirect

# Store the original admin index view
original_index = admin.site.index

def custom_admin_index(request, extra_context=None):
    """Redirect admin index to main app only if user came from successful login"""
    # Check if this is a redirect from a successful login
    referrer = request.META.get('HTTP_REFERER', '')
    
    # Only redirect if:
    # 1. Referrer is specifically the admin login page
    # 2. AND this is a GET request (post-login redirect)
    # 3. AND there's no 'next' parameter (which would indicate intentional admin access)
    if (request.method == 'GET' and 
        '/admin/login/' in referrer and 
        not request.GET.get('next')):
        # This appears to be a post-login redirect, send to main app
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    
    # Otherwise, show normal admin index (direct admin access, bookmarks, etc.)
    return original_index(request, extra_context)

# Replace the admin index method
admin.site.index = custom_admin_index

# Register your models here.
logger = logging.getLogger(__name__)


class ItemInline(admin.TabularInline):
    ordering=['start']
    model = Item
    
class TsPlotPointInline(admin.TabularInline):
    ordering=['date']
    model = TimeSeriesPlotPoint


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    inlines =[ItemInline,TsPlotPointInline]
    
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    ordering=['start']
    
    
class TimeSeriesPlotPointResource(ModelResource) :
  
    def __init__(self, **kwargs):
        super().__init__()        
        
    def before_save_instance(self, instance, row, **kwargs):
        if "track_id" in row:                
            instance.track_id = row['track_id']
            logger.info("added track id to instance {}".format(instance.track_id))
        else:
            logger.warn("could not find a track_id in row")            
    
    def before_import_row(self,row,**kwargs):    
        chars = "1234567890"
        randid = ''.join(random.choice(chars) for _ in range(10))
        request_track_id = kwargs.get('request').POST.get('track')
        row["id"]=randid   
        if (request_track_id is not None):            
            logger.debug(''.format('found track{}',request_track_id))
            self.track_id = request_track_id
            row["track_id"] = request_track_id
        else:
            logger.warn('could not find track id')
    
    class Meta:
        model =TimeSeriesPlotPoint
        name="Import time series plot points"   
       
    
    
@admin.register(TimeSeriesPlotPoint)
class TimeSeriesAdmin(ImportMixin,admin.ModelAdmin):
    resource_class = TimeSeriesPlotPointResource
    import_form_class = CustomTimeSeriesPlotPointImportForm 
    confirm_form_class = CustomConfirmTimeSeriesPlotPointImportForm
    
    
    
    def get_confirm_form_initial(self, request, import_form):
        initial = super().get_confirm_form_initial(request, import_form)

        # Pass on the `track_id` value from the import form to
        # the confirm form (if provided)
        if import_form:
            track_id_param = import_form.cleaned_data['track'].id
            logger.info('adding track id  to kwargs')
            initial['track'] = track_id_param
        return initial    
    
            
            
    
    
    

    
     
    
    
    