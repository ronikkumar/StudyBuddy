from email import message
from email.policy import default
from multiprocessing import context
from unicodedata import name
from venv import create
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.db.models import Q
from .models import Message, Room, Topic, User
from .forms import RoomForm, UserForm, MyUserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
# Create your views here.



def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('Home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('Home')
        else:
            messages.error(request, 'Username OR password does not exit')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def registerPage(request):
    form=MyUserCreationForm()
    if request.method=='POST':
        form=MyUserCreationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.username=user.username.lower()
            user.save()
            login(request, user)
            return redirect('Home')
        else:
            messages.error(request, "An error occurred during registeration")
    return render(request, 'base/login_register.html', {'form':form})

def logoutUser(request):
    logout(request)
    return redirect('Home')
    
def Home(request):
    q=request.GET.get('q') if request.GET.get('q') != None else  ''
    rooms=Room.objects.filter(
        Q(topic__name__icontains=q)|
        Q(name__icontains=q)|
        Q(desccription__icontains=q)
    )
    topics=Topic.objects.all()[0:5]
    room_count=rooms.count()
    room_messages=Message.objects.filter(Q(room__topic__name__icontains=q))
    context={'rooms':rooms, 'topics':topics, 'room_count':room_count, "room_messages":room_messages}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room=Room.objects.get(id=pk)
    room_messages=room.message_set.all().order_by('-created')
    participants=room.participants.all()
    if request.method=='POST':
        message=Message.objects.create(
            user=request.user, 
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context={'room':room, 'room_messages':room_messages, "participants":participants}
    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user=User.objects.get(id=pk)
    rooms=user.room_set.all()
    room_messages=user.message_set.all()
    topics=Topic.objects.all()
    context={"user":user, "rooms":rooms, "room_messages":room_messages, "topics":topics}
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')  #2h44m
def createRoom(request):
    form=RoomForm()
    topics=Topic.objects.all()
    if(request.method=='POST'):
        topic_name=request.POST.get('topic')
        topic, created=Topic.objects.get_or_create(name=topic_name)
        form=RoomForm(request.POST)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            desccription=request.POST.get('desccription')
        )
        return redirect('Home')

    context={'form':form, 'topics':topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')  #2h44m
def updateRoom(request, pk):
    room=Room.objects.get(id=pk)
    form=RoomForm(instance=room)
    topics=Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("You're not allowed here!")
    
    if request.method=='POST':
        topic_name=request.POST.get('topic')
        topic, created=Topic.objects.get_or_create(name=topic_name)
        room.name=request.POST.get('name')
        room.topic=topic
        room.desccription=request.POST.get('desccription')
        room.save()
        return redirect('Home')
    
    context={ 'form':form, 'topics':topics, 'room':room }
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')  #2h44m
def deleteRoom(request, pk):
    room=Room.objects.get(id=pk)

    if request.user !=  room.host:
        return HttpResponse("You are not allowed here!")

    if request.method=='POST':
        room.delete()
        return redirect('Home')
    
    return render(request, 'base/delete.html', {'obj':room})

@login_required(login_url='login')  #2h44m
def deleteMessage(request, pk):
    message=Message.objects.get(id=pk)

    if request.user !=  message.user:
        return HttpResponse("You are not allowed here!")

    if request.method=='POST':
        message.delete()
        return redirect('Home')
    
    return render(request, 'base/delete.html', {'obj':message})

@login_required(login_url='login')  #2h44m
def updataUser(request):
    user=request.user
    form=UserForm(instance=user)

    if request.method=='POST':
        form=UserForm(request.POST, request.FILES ,instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update-user.html', {'form':form})

def topicsPage(request):
    q=request.GET.get('q') if request.GET.get('q') != None else  ''
    topics=Topic.objects.filter(name__icontains=q)
    #context={'topics':topics}
    return render(request, 'base/topics.html', {"topics":topics})

def activityPage(request):
    room_messages=Message.objects.all()
    return render(request, 'base/activity.html', {"room_messages":room_messages})