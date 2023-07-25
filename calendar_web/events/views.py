from django.shortcuts import render, redirect
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from django.http import HttpResponseRedirect
from .models import Event, Venue
# импортируем пользователя из django
from django.contrib.auth.models import User
from .forms import VenueForm, EventForm, EventFormAdmin
from django.http import HttpResponse
import csv
from django.contrib import messages

from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import telegram


# создаем страницу подтверждения администратором
def admin_approval(request):
    event_list = Event.objects.all().order_by('-event_date')
    if request.user.is_superuser:
        if request.method == 'POST':
            id_list = request.POST.getlist('boxes')

            event_list.update(approved=False)
            # обновим БД
            for x in id_list:
                Event.objects.filter(pk=int(x)).update(approved=True)

            messages.success(request, 'Подтверждение списка было обновлено')
            return redirect('events')

        else:
            return render(request, 'events/admin_approval.html', {'event_list': event_list} )
    else:
        messages.success(request, 'У вас нет доступа к просмотру этой страницы')
        return redirect('home')

    return render(request, 'events/admin_approval.html')

# создаем страницу мои мероприятия
def my_events(request):
    if request.user.is_authenticated:
        me = request.user.id
        events = Event.objects.filter(manager=me)
        return render(request, 'events/my_events.html', {
            'events': events
        })
    else:
        messages.success(request, ('Вы не можете просмотреть эту страницу.'))
        return redirect('home')


# создаем пдф файл списка мест мероприятий
def venue_pdf(request):
    # создаем буфер байтового потока
    buf = io.BytesIO()
    # создаем холст
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    # создаем текстовый объект
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
    textob.setFont('Arial', 14)

    # обозначим модель
    venues = Venue.objects.all()
    # создаем пустой словарь
    lines = []
    for venue in venues:
        lines.append(venue.name)
        lines.append(venue.address)
        lines.append(venue.phone)
        lines.append(venue.web)
        lines.append('____________________')

    for line in lines:
        textob.textLine(line)
    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename='места_пдф')


# создаем текстовый файл со списком мест проведения
def venue_text(request):
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=места_проведения.txt'
    # обозначаем модель
    venues = Venue.objects.all()
    # создаем пустой словарь
    lines = []
    # цикл ввода и вывода
    for venue in venues:
        lines.append(f'{venue.name}\n{venue.address}\n{venue.phone}\n{venue.web}\n\n')

    # записываем в текстовый файл
    response.writelines(lines)
    return response


# удалить место проведения
def delete_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    venue.delete()
    return redirect('list-venues')


# удалить мероприятие
def delete_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    if request.user == event.manager:
        event.delete()
        messages.success(request, ('Мероприятие удалено.'))
        return redirect('events')
    else:
        messages.success(request, ('Вы не можете удалить это событие.'))
        return redirect('events')


# изменить мероприятие
def update_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    if request.user.is_superuser:
        form = EventFormAdmin(request.POST or None, instance=event)
    else:
        form = EventForm(request.POST or None, instance=event)
    if form.is_valid():
        form.save()
        return redirect('events')

    return render(request, 'events/update_event.html', {'event': event,
                                                        'form': form})

# отправление уведомлений с помощью телеграм бота в канал
def send_message_to_channel(message):

    bot = telegram.Bot(token='6095875871:AAEIF_qi7qnXo59lfFsWxPNAE_Zn4_I_YdM')
    site_url = "http://sergeysmnv.pythonanywhere.com/"
    message_with_link = "{}\n\nСсылка на сайт: {}".format(message, site_url)
    bot.send_message(chat_id='-1001745287542', text=message_with_link)

# добавить мероприятие
def add_event(request):
    submitted = False
    if request.method == 'POST':
        if request.user.is_superuser:
            form = EventFormAdmin(request.POST)
            if form.is_valid():
                form.save()
                send_message_to_channel("Добавлено новое мероприятие на сайте: {}".format(form.cleaned_data['name']))
                return HttpResponseRedirect('/add_event?submitted=True')
        else:
            form = EventFormAdmin(request.POST)
            if form.is_valid():
                # form.save()
                event = form.save(commit=False)
                event.manager = request.user  # вошедший в систему пользователь
                event.save()
                send_message_to_channel("Добавлено новое мероприятие на сайте: {}".format(event.name))
                return HttpResponseRedirect('/add_event?submitted=True')
    else:
        # переходим на страницу без отправления заявки
        if request.user.is_superuser:
            form = EventFormAdmin
        else:
            form = EventForm

        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'events/add_event.html', {'form': form, 'submitted': submitted})


# изменить место проведения
def update_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    form = VenueForm(request.POST or None, request.FILES or None, instance=venue)
    if form.is_valid():
        form.save()
        return redirect('list-venues')
    return render(request, 'events/update_venue.html', {'venue': venue,
                                                        'form': form})


# поиск мест проведения
def search_venues(request):
    if request.method == 'POST':
        searched = request.POST['searched']
        venues = Venue.objects.filter(name__contains=searched)

        return render(request, 'events/search_venues.html', {'searched': searched, 'venues': venues})
    else:
        return render(request, 'events/search_venues.html', {})


def show_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    venue_owner = User.objects.get(pk=venue.owner)
    return render(request, 'events/show_venue.html', {'venue': venue,
                                                      'venue_owner': venue_owner
                                                      })


def list_venues(request):
    venue_list = Venue.objects.all().order_by('name')
    return render(request, 'events/venue.html', {'venue_list': venue_list})


# добавить место проведения
def add_venue(request):
    submitted = False
    if request.method == 'POST':
        form = VenueForm(request.POST, request.FILES)
        if form.is_valid():
            venue = form.save(commit=False)
            venue.owner = request.user.id  # вошедший в систему пользователь
            venue.save()
            # form.save()
            return HttpResponseRedirect('/add_venue?submitted=True')
    else:
        form = VenueForm
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'events/add_venue.html', {'form': form, 'submitted': submitted})


def all_events(request):
    event_list = Event.objects.all().order_by('event_date')
    return render(request, 'events/event_list.html', {'event_list': event_list})


def home(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
    name = 'Kate'
    month = month.title()

    # переименовываем месяц из названия в число
    month_number = list(calendar.month_name).index(month)
    month_number = int(month_number)

    # создаем календарь
    cal = HTMLCalendar().formatmonth(year, month_number)

    # переходим к текущему году
    now = datetime.now()
    current_year = now.year

    # запрашиваем модель событий для дат
    event_list = Event.objects.filter(
        event_date__year=year,
        event_date__month=month_number
    )

    # текущее время
    time = now.strftime('%I:%M %p')

    return render(request,
                  'events/home.html', {
                      'name': name,
                      'year': year,
                      'month': month,
                      'month_number': month_number,
                      'cal': cal,
                      'current_year': current_year,
                      'time': time,
                      'event_list': event_list,

                  }
                  )
