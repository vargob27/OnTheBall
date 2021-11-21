import requests
from django.shortcuts import render, redirect
from django.contrib import messages, admin
from .models import *
from datetime import date
import bcrypt

def index(request):
    if 'user_id' in request.session:
        return redirect('/home')
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        errors = User.objects.registration_validator(request.POST)
        if len(errors) != 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/')
    # hash password
        hashed_pw = bcrypt.hashpw(
            request.POST['password'].encode(), bcrypt.gensalt()).decode()
    # create User
        new_user = User.objects.create(
            first_name=request.POST['first_name'], 
            last_name=request.POST['last_name'], 
            email=request.POST['email'], 
            password=hashed_pw,
            dob=request.POST['dob'],
            location=request.POST['location'],
        )
    # create session
        request.session['user_id'] = new_user.id
        return redirect('/home')
    return redirect('/')

def login(request):
    if request.method == "POST":
        errors = User.objects.login_validator(request.POST)
        if len(errors) != 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/')
        this_user = User.objects.filter(email=request.POST['email'])
        request.session['user_id'] = this_user[0].id
        return redirect('/home')
    return redirect('/')

def logout(request):
    request.session.flush()
    return redirect('/home')

def success(request):
    if 'user_id' not in request.session:
        return render(request, 'index.html')
    this_user = User.objects.filter(id=request.session['user_id'])
    context = {
        'user': this_user[0],
    }
    return render(request, 'index.html', context)

def comment(request, event_id):
    if 'user_id' not in request.session:
        return redirect('/')
    event = Event.objects.get(id=event_id)
    Comment_Thread.objects.create(
        message=request.POST['message'],
        poster=User.objects.get(id=request.session['user_id']),
        event= event
        )
    return redirect(f'/event/{event_id}')

def editComment(request, event_id, post_id):
    if 'user_id' not in request.session:
        return redirect('/')
    context = {
        'comment': Comment_Thread.objects.get(id=post_id),
        'event': Event.objects.get(id=event_id)
    }
    return render(request, 'editComment.html', context)

def updateComment(request, event_id, post_id):
    if 'user_id' not in request.session:
        return redirect('/')
    event = event_id
    to_update = Comment_Thread.objects.get(id=post_id)
    to_update.message = request.POST['message']
    to_update.save()
    return redirect(f'/event/{event}')

def deleteComment(request, event_id, post_id):
    if 'user_id' not in request.session:
        return redirect('/')
    event = event_id
    to_delete = Comment_Thread.objects.get(id=post_id)
    if request.session['user_id'] != to_delete.poster.id:
        messages.error(request, 'You are not the creator of the comment you are trying to delete!')
        return redirect(f'/event/{event}')
    to_delete.delete()
    return redirect(f'/event/{event}')

def add_like(request, event_id, id):
    if 'user_id' not in request.session:
        return redirect('/')
    liked_message = Comment_Thread.objects.get(id=id)
    user_liking = User.objects.get(id=request.session['user_id'])
    liked_message.likes.add(user_liking)
    return redirect(f'/event/{event_id}')

def remove_like(request, event_id, id):
    if 'user_id' not in request.session:
        return redirect('/')
    liked_message = Comment_Thread.objects.get(id=id)
    user_liking = User.objects.get(id=request.session['user_id'])
    liked_message.likes.remove(user_liking)
    return redirect(f'/event/{event_id}')

def profile(request, user_id):
    user = User.objects.get(id=user_id)
    age = date.today() - user.dob
    yearsOld = int((age).days / 365.25)
    print(yearsOld)
    context = {
        'user': User.objects.get(id=user_id),
        'events': user.createdEvents.all(),
        'loggedIn': User.objects.get(id=request.session['user_id']),
        'age': yearsOld
    }
    
    return render(request, 'profile.html', context)

def edit_profile(request, user_id):
    if 'user_id' not in request.session:
        return redirect('/')
    checkID = request.session['user_id']
    if checkID != user_id:
        return redirect('/home')
    context = {
        'user': User.objects.get(id=user_id),
        'loggedIn': request.session['user_id'],
    }
    return render(request, 'editProfile.html', context)

def update_profile(request, user_id):
    if 'user_id' not in request.session:
        return redirect('/')
    checkID = request.session['user_id']
    if checkID != user_id:
        return redirect('/home')
    errors = User.objects.update_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
            return redirect(f'/user/edit/{user_id}')
    to_update = User.objects.get(id=user_id)
    to_update.first_name = request.POST['first_name']
    to_update.last_name = request.POST['last_name']
    to_update.email = request.POST['email']
    to_update.dob = request.POST['dob']
    to_update.location = request.POST['location']
    to_update.save()
    return redirect(f'/user/{user_id}')

def allEvents(request):
    sorted_events = Event.objects.all().order_by('day')
    context = {
        'events': sorted_events,
    }
    return render(request, 'allEvents.html', context)

def event(request, event_id):
    if 'user_id' not in request.session:
        event = Event.objects.get(id=event_id)
        cityname = event.city
        apikey = 'c34754078c4106b2991a642eea434c58'
        url = f'http://api.openweathermap.org/data/2.5/weather?q={cityname}&units=imperial&appid={apikey}'
        r = requests.get(url).json()
        city_weather = {
            'city' : cityname,
            'temperature' : r['main']['temp'],
            'description' : r['weather'][0]['description'],
            'icon' : r['weather'][0]['icon'],
            }
        weather_data = []
        weather_data.append(city_weather)

        context = {
            'event': Event.objects.get(id=event_id),
            'weather_data' : weather_data,
            'comments': event.event_messages.all()
            }
        return render(request, 'event.html', context)
    event = Event.objects.get(id=event_id)
    cityname = event.city
    apikey = 'c34754078c4106b2991a642eea434c58'
    url = f'http://api.openweathermap.org/data/2.5/weather?q={cityname}&units=imperial&appid={apikey}'
    r = requests.get(url).json()
    city_weather = {
        'city' : cityname,
        'temperature' : r['main']['temp'],
        'description' : r['weather'][0]['description'],
        'icon' : r['weather'][0]['icon'],
        }
    weather_data = []
    weather_data.append(city_weather)

    context = {
        'user': User.objects.get(id=request.session['user_id']),
        'event': Event.objects.get(id=event_id),
        'loggedIn': User.objects.get(id=request.session['user_id']),
        'weather_data' : weather_data,
        'comments': event.event_messages.all()
        }
    return render(request, 'event.html', context)

def createEvent(request):
    if 'user_id' not in request.session:
        return redirect('/')
    now = datetime.today().strftime('%Y-%m-%d')
    errors = Event.objects.event_validator(request.POST)
    if len(errors) != 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/home')
    if request.POST['day'] < now:
        messages.error(request, 'Date cannot be in the past')
        return redirect('/home')
    Event.objects.create(
        title = request.POST['title'],
        description = request.POST['description'],
        sport = request.POST['sport'].lower(),
        city = request.POST['city'],
        address = request.POST['address'],
        day = request.POST['day'],
        creator = User.objects.get(id=request.session['user_id'])
    )
    return redirect('/home')

def editEvent(request, event_id):
    if 'user_id' not in request.session:
        return redirect('/')
    context = {
        'event': Event.objects.get(id=event_id),
        'loggedIn': User.objects.get(id=request.session['user_id']),
    }
    return render(request, 'editEvent.html', context)

def updateEvent(request, event_id):
    if 'user_id' not in request.session:
        return redirect('/')
    # now = datetime.today().strftime('%Y-%m-%d')
    # errors = Event.objects.update_event_validator(request.POST)
    # if len(errors) != 0:
    #     for key, value in errors.items():
    #         messages.error(request, value)
    #     print(request.POST['title'])
    #     return redirect(f'/event/{event_id}/edit')
    # if request.POST['day'] < now:
    #     messages.error(request, 'Date cannot be in the past')
    #     return redirect(f'/event/{event_id}/update')
    to_update = Event.objects.get(id=event_id)
    to_update.title = request.POST['title']
    to_update.description = request.POST['description']
    to_update.sport = request.POST['sport'].lower()
    to_update.city = request.POST['city']
    to_update.address = request.POST['address']
    to_update.day = request.POST['day']
    to_update.save()
    return redirect(f'/event/{event_id}')

def deleteEvent(request, event_id):
    if 'user_id' not in request.session:
        return redirect('/')
    to_delete = Event.objects.get(id=event_id)
    if request.session['user_id'] != to_delete.creator.id:
        messages.error(request, 'You are not the creator of the Event you are trying to delete!')
        return redirect('/home')
    to_delete.delete()
    return redirect('/home')

def attendEvent(request, event_id):
    if 'user_id' not in request.session:
        return redirect('/home')
    eventToAttend = Event.objects.get(id=event_id)
    userToAttend = User.objects.get(id=request.session['user_id'])
    eventToAttend.attending.add(userToAttend)
    return redirect(f'/event/{event_id}')

def unattendedEvent(request, event_id):
    if 'user_id' not in request.session:
        return redirect('/')
    loggedIN = request.session['user_id']
    event = Event.objects.get(id=event_id)
    event.attending.remove(loggedIN)
    return redirect(f'/event/{event_id}')

def find(request, sport):
    if 'user_id' not in request.session:
        sorted_events = Event.objects.filter(sport=sport)
        context = {
            'events': sorted_events,
        }
        return render(request, 'sortedEvents.html', context)
    sorted_events = Event.objects.filter(sport=sport)
    this_user = User.objects.filter(id=request.session['user_id'])
    context = {
        'events': sorted_events,
        'user': this_user[0],
    }
    return render(request, 'sortedEvents.html', context)

def test(request):
    return render(request, 'index.html')