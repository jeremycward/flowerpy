from django.db import models

# Create your models here.
from django.db import models
from datetime import date
import copy
# Create your models here.
class Track(models.Model):
    EVENT="EVE"
    SEGMENT="SEG"
    TIMESERIES="TSE"
    SERIES="SER"
    TRACK_TYPE_CHOICES={
        EVENT: "Event",
        SEGMENT: "Segment",
        SERIES: "Series",
        TIMESERIES: "TimeSeries"        
    }
    name = models.CharField(max_length=100)    
    itemType = models.CharField(max_length=3,choices=TRACK_TYPE_CHOICES, default=SERIES)        
    
    def __str__(self):
        return 'Track:' + self.name + 'Id:' + str(self.id)
    
    def items(self):
        return Item.objects.filter(track__id__exact=self.id).order_by('start','startTime')
    
    
    
    def event_items(self):
        return Item.objects.filter(track__id__exact=self.id).order_by('start','startTime')
    
    def time_series_items(self):
        return TimeSeriesPlotPoint.objects.filter(track__id__exact=self.id).order_by("date")

    



class Item(models.Model):    
    track = models.ForeignKey(Track, on_delete=models.CASCADE)    
    name = models.CharField(max_length=100) 
    detail1= models.CharField(max_length=100,blank=True,null=True)   
    detail2= models.CharField(max_length=100,blank=True,null=True)   
    start =models.DateField()    
    end = models.DateField(null=True,blank=True )
    startTime = models.TimeField(null=True,blank=True)
    endTime = models.TimeField(null=True,blank=True)
    img = models.URLField(max_length=500,blank=True, null=True)
    additional_info = models.URLField(max_length=500,blank=True, null=True)
    def __str__(self):
        return 'Item:' + self.name + ":" + str(self.start)
    
    
class TimeSeriesPlotPoint(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE)        
    date= models.DateField()
    value= models.FloatField()
