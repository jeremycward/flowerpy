from django.shortcuts import render

# Create your views here.
import json
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Track, Item
from django.utils.safestring import SafeString
# Create your views here.

def index(request):
   tracks = []  
   itemWidgetsJson = []
   template = loader.get_template("flowerapp/flower.html")
   context = {
       "timeline_data" : Track.objects.all()
   }

   return HttpResponse(template.render(context, request))


    
        
    