from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
import json
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Track, Item
from django.utils.safestring import SafeString
# Create your views here.

@login_required
def home(request):
   tracks = []  
   itemWidgetsJson = []
   template = loader.get_template("flowerapp/flower.html")
   context = {
       "timeline_data" : Track.objects.all()
   }

   return HttpResponse(template.render(context, request))


    
        
    