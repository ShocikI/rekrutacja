import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from datetime import date, timedelta, datetime
from calendar import monthrange
from rekrutacja import settings


# Create your views here.
def start(request):
    today = date.today()
    year = today.year
    month = today.month

    return redirect(reverse(calendar_view, kwargs={'year':year, 'month':month}))
    
def calendar_view(request, year, month):
    # Połączenie z API
    all_events = get_events()

    # Dane do poprawnych zmian miesięcy w kalendarzu
    current_month_name, previous_month, previous_year, next_month, next_year = get_date_data(year, month)
    
    # Ustal pierwszy dzień miesiąca i liczbę dni w miesiącu
    first_day_of_month, num_days_in_month = monthrange(year, month)
    
    # Przygotowanie listy pustych dni przed pierwszym dniem miesiąca
    empty_days = list(range(first_day_of_month))

    # Przygotowanie danych do kalendarza
    calendar_data = {
        'month_name': current_month_name,
        'empty_days': empty_days,
    }

    # Przygotowanie słownika, gdzie kluczem będzie dzień, a wartością lista wydarzeń
    events_by_day = {day: [] for day in range(1, num_days_in_month + 1)}

    # Jeśli nie udało się połączyć z API wyświetlany jest 'pusty' kalendarz + error
    if all_events is None:
        return render(request, 'calendar_view.html', {
            'year':year, 
            'month':month, 
            'calendar': calendar_data, 
            'events': events_by_day,
            'previous_year': previous_year,
            'next_year': next_year,
            'previous_month': previous_month,
            'next_month': next_month,
            'error': 'Failed to fetch data'
        })

    # Przygotowanie listy wydarzeń na bieżący miesiąc
    events_in_month = []

    # Przetwarzanie wydarzeń
    for event in all_events:
        event_start_date = datetime.strptime(event['start_time'], '%Y-%m-%dT%H:%M:%S')
        if event_start_date.month == month and event_start_date.year == year:
            duration = event['duration']
            for i in range(duration):
                new_day = event_start_date + timedelta(days=i)
                events_in_month.append({
                    'id': event['id'],
                    'name': event['name'],
                    'start_date': new_day,
                    'actual_duration': i
                })
    
    # Przypisanie wydarzeń do konkretnego dnia
    for event in events_in_month:
        for i in range(1, len(events_by_day)+1):
            if event['start_date'].day == i:
                events_by_day[i].append(event)

    return render(request, 'calendar_view.html', {
        'year':year, 
        'month':month, 
        'calendar': calendar_data,
        'events':events_by_day, 
        'previous_year': previous_year,
        'next_year': next_year,
        'previous_month': previous_month,
        'next_month': next_month,
    })
    

def day_view(request, year, month, day):
    # Połączenie z API
    all_events = get_events()

    # Przygotowanie danych do poprawnych zmian miesięcy w kalendarzu
    current_month_name, *_ = get_date_data(year, month)
    calendar_data = {
        'month_name': current_month_name,
    }

    # Jeśli nie połączyło się z API wyświetla error
    if all_events is None:
        return render(request, 'day_view.html', {
            'year':year, 
            'month': month, 
            'day': day,
            'calendar': calendar_data,
            'error': 'Failed to fetch data'
        })
    
    # Przygotowanie danych do wyświetlenia na stronie
    day_events = []
    for event in all_events:
        event_start_date = datetime.strptime(event['start_time'], '%Y-%m-%dT%H:%M:%S')
        duration = event['duration']
        finish_day = event_start_date + timedelta(days=duration-1)
        if (
            event_start_date.year == year 
            and event_start_date.month == month 
            and event_start_date.day <= day <= finish_day.day
        ):
            current_event = get_event_by_id(event_id=event['id'])
            if current_event != None:
                event_minute = f"0{event_start_date.minute}" if event_start_date.minute < 10 else f"{event_start_date.minute}"
                start_time = f"{event_start_date.hour}:{event_minute}"
                tags = [tag for tag in current_event['tags']]
                day_events.append({
                    'id': current_event['id'],
                    'name': current_event['name'],
                    'start_time': start_time,
                    'short_description': current_event['short_description'],
                    'long_description': current_event['long_description'],
                    'link': current_event['registration_link'],
                    'tags': tags,
                    'image_url': f"{settings.BASE_URL}/{current_event['image_url']}"
                })

    return render(request, 'day_view.html', {
        'year': year, 
        'month': month, 
        'day': day,
        'day_events': day_events,
        'calendar': calendar_data
    })
    
# Połączenia z API
def get_events():
    url = f"{settings.BASE_URL}/events"
    headers = {
        'api-key': settings.API_KEY,
    }
    response = requests.get(url, headers=headers)
    status_code = response.status_code
    
    if status_code == 200:
        return response.json()
    else:
        return None


def get_event_by_id(event_id:int):
    url = f"{settings.BASE_URL}/events/{event_id}"
    headers = {
        'api-key': settings.API_KEY,
    }
    response = requests.get(url, headers=headers)
    status_code = response.status_code

    if status_code == 200:
        return response.json()
    else:
        return None

# Funkcje użytkowe
def get_month_name(month: int) -> str:
    match month:
        case 1: return "Styczeń"
        case 2: return "Luty"
        case 3: return "Marzec"
        case 4: return "Kwiecień"
        case 5: return "Maj"
        case 6: return "Czerwiec"
        case 7: return "Lipiec"
        case 8: return "Sierpień"
        case 9: return "Wrzesień"
        case 10: return "Październik"
        case 11: return "Listopad"
        case 12: return "Grudzień"


def get_date_data(year: int, month: int) -> tuple:
    # Sprawdzamy overlap month
    if month < 1 or month > 12: 
        year_decrease = int(month / 12)
        year += year_decrease
        month = month % 12

    # Obliczamy poprzedni i następny miesiąc
    if month == 1:
        previous_month = 12
        previous_year = year - 1
    else:
        previous_month = month - 1
        previous_year = year

    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    month_name = get_month_name(month)

    return month_name, previous_month, previous_year, next_month, next_year
