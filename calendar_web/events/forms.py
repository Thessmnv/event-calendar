from django import forms
from django.forms import ModelForm
from .models import Venue, Event

# форма мероприятия для администратора
class EventFormAdmin(ModelForm):
    class Meta:
        model = Event
        fields = ('name', 'event_date', 'venue', 'manager', 'attendees', 'description' )
        labels = {
            'name': '',
            'event_date': '',
            'venue': '',
            'manager': '',
            'attendees': '',
            'description': '',
         }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название мероприятия'}),
            'event_date': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Дата и время'}),
            'venue': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Место'}),
            'manager': forms.Select(attrs={'class': 'form-select', 'placeholder': 'Организатор'}),
            'attendees': forms.SelectMultiple(attrs={'class': 'form-control', 'placeholder': 'Участники'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Описание'}),

        }


# # форма мероприятия для пользователя
class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ('name', 'event_date', 'venue',  'attendees', 'description' )
        lables = {
            'name': '',
            'event_date': '',
            'venue': '',
            'attendees': '',
            'description': '',
         }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название мероприятия'}),
            'event_date': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Дата и время'}),
            'venue': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Место'}),
            'attendees': forms.SelectMultiple(attrs={'class': 'form-control', 'placeholder': 'Участники'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Описание'}),

        }


# Создаем форму места проведения
class VenueForm(ModelForm):
    class Meta:
        model = Venue
        fields = ('name', 'address', 'phone', 'web', 'venue_image')
        labels = {
            'name': '',
            'address': '',
            'phone': '',
            'web': '',
            'venue_image':'',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название места'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Адрес'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Телефон'}),
            'web': forms.TextInput (attrs={'class': 'form-control', 'placeholder': 'Веб-сайт'}),
        }
