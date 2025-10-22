
from django import template
from ..models import Track,Item
register = template.Library()
import datetime as dt
from datetime import timedelta
from dataclasses import dataclass

timeFormat = "%Y-%m-%d %H:%M:%S"


@register.inclusion_tag("flowerapp/htmlx/time_series_track.html")
def TSE_track(track):
    return {
           "track" : TSE_track_constructor(track)
    }
    
    

@register.inclusion_tag("flowerapp/time_series_track.html")
def time_series_track(track):
    if len(track.time_series_items())==0:
        return {}
    norm_pp = build_normalised_plot_points(track.time_series_items())
    norm_track = NormalisedTimeSeriesTrack(
        start=dfmt(norm_pp[0].pp.date),
        end=dfmt(norm_pp[len(norm_pp)-1].pp.date),
        correlationId = track.id,
        track=track,
        name=track.name,
        normalisedPlotPoints= norm_pp)
    return {"normalised_track" :  norm_track}

@register.inclusion_tag("flowerapp/timeline.html")
def timeline_data():
    return {"tracks" : Track.objects.all()}
    
@register.inclusion_tag("flowerapp/event_track.html")
def event_track(track):
    return {"eventTrack" : SequencedEventTrack(track)}        

@register.inclusion_tag("flowerapp/htmlx/event_track.html")
def EVE_track(track):
    return {"track" :  EVE_track_constructor(track)}        


def build_seq_items_from_model_items(model_items):
    items:list[SequencedEventItem] = []
    for idx,thisItem in enumerate(model_items):                          
          nextItem = None if  idx+1 >= len(model_items)  else model_items[idx+1]                    
          sei = SequencedEventItem(              
          )
          items.append(TimelineItemWidget(thisItem,nextItem,groupId,itemContent))          
    return items      


        
    
    
@dataclass
class SequencedEventItem:
    item: Item
    start:str
    end:str

    
    def __init__(self,item,nextItem):
        self.item = item
        self.start = tfmt(date_time_combine(item.start,item.startTime))
        if (item.end is not None):
            self.end = tfmt(date_time_combine(item.end,item.endTime))
        else:
            if (nextItem is not None and nextItem.start is not None):
                self.end = tfmt(date_time_combine(nextItem.start, nextItem.startTime))
            else:
                self.end = None    

        
@dataclass
class SequencedEventTrack:
    track: Track
    items: list[SequencedEventItem]
    def __init__(self,track):
        self.track = track
        items:list[SequencedEventItem] = []
        model_items = track.event_items()
        for idx,thisItem in enumerate(model_items):                          
          nextItem = None if  idx+1 >= len(model_items)  else model_items[idx+1]                              
          items.append(SequencedEventItem(thisItem,nextItem))             
        self.items =items


@register.inclusion_tag("flowerapp/track_items_delegator.html")
def render_track_items(track_type, track_data):
    """
    Custom template tag that renders track items based on track type.
    
    Usage in template:
    {% load flower_tags %}
    {% render_track_items track_type track_data %}
    
    Args:
        track_type: String indicating the type of track ("sequence", "TSE", "eventline")
        track_data: The track object or data containing items to render
    """
    template_name = get_track_template_name(track_type)
    
    return {
        'track_type': track_type,
        'track_data': track_data,
        'track': track_data,  # For backward compatibility
        'track_items_template': template_name
    }


@register.simple_tag
def get_track_template_name(track_type):
    """
    Simple tag that returns the appropriate template name based on track type.
    
    Usage in template:
    {% get_track_template_name track_type as template_name %}
    {% include template_name with track=track_data %}
    """
    template_mapping = {
        'SER': 'flowerapp/track_items_sequence.html',
        'TSE': 'flowerapp/track_items_tse.html', 
        'EVE': 'flowerapp/track_items_eventline.html',
    }
    return template_mapping.get(track_type, 'flowerapp/track_items_sequence.html')


@register.filter
def get_track_items_by_type(track, track_type):
    """
    Filter that returns appropriate items based on track type.
    
    Usage in template:
    {% for item in track|get_track_items_by_type:track_type %}
    """
    if track_type == 'sequence':
        return track.event_items() if hasattr(track, 'event_items') else []
    elif track_type == 'TSE':
        return track.time_series_items() if hasattr(track, 'time_series_items') else []
    elif track_type == 'eventline':
        return track.event_items() if hasattr(track, 'event_items') else []
    else:
        return []

@register.filter
def format_item_datetime(dt_obj):    
    return dt_obj.strftime(timeFormat)
    

@register.simple_tag
def derive_end_date(itemList, itemIndex):
    """
    Derives end date for an item based on its position in the list.
    
    Args:
        itemList: Complete list of items
        itemIndex: Index of the current item in the list
    
    Returns:
        String: Formatted date in "YYYY-MM-DD HH:MM:SS" format
        
    Logic:
        - If current item has an end date: return formatted end date
        - If current item has no end date and is not last: return next item's start date
        - If current item is last and has no end date: return today + 1 week
    """
    timeFormat = "%Y-%m-%d %H:%M:%S"
    
    if not itemList or itemIndex >= len(itemList) or itemIndex < 0:
        # Invalid input, return today + 1 week as fallback
        fallback_date = dt.datetime.now() + timedelta(weeks=1)
        return fallback_date.strftime(timeFormat)
    
    current_item = itemList[itemIndex]
    
    # If current item has an end date, use it
    if current_item.end is not None:
        # Combine end date with end time (or default time)
        end_time = current_item.endTime if current_item.endTime else dt.time(23, 59, 59)
        end_datetime = dt.datetime.combine(current_item.end, end_time)
        return end_datetime.strftime(timeFormat)
    
    # Current item has no end date
    # If not the last item, use next item's start date
    if itemIndex < len(itemList) - 1:
        next_item = itemList[itemIndex + 1]
        # Combine start date with start time (or default time)
        start_time = next_item.startTime if next_item.startTime else dt.time(0, 0, 0)
        start_datetime = dt.datetime.combine(next_item.start, start_time)
        return start_datetime.strftime(timeFormat)
    
    # Current item is last and has no end date: use today + 1 week
    fallback_date = dt.datetime.now() + timedelta(weeks=1)
    return fallback_date.strftime(timeFormat)
