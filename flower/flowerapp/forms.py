from django import forms
from import_export.forms import (
    ConfirmImportForm,
    ImportForm,
    SelectableFieldsExportForm,
)
from .models import Track
class CustomTimeSeriesPlotPointImportFormMixin(forms.Form):
    track = forms.ModelChoiceField(queryset=Track.objects.all(), required=True)


class CustomTimeSeriesPlotPointImportForm(CustomTimeSeriesPlotPointImportFormMixin,ImportForm):
    pass
    
class CustomConfirmTimeSeriesPlotPointImportForm (CustomTimeSeriesPlotPointImportFormMixin, ConfirmImportForm) :
    pass