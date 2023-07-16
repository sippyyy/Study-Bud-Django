from django.db.models import Q
from django.shortcuts import render,redirect
from .models import Room,Topic,Message,User
from .forms import RoomForm,UserForm,MyUserCreationForm
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required


def loginPage(request):
    page='login'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        username = request.POST.get('email').lower()
        password = request.POST.get('password')
        try:
            user= User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')
            
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, 'Username or Password is incorrect')
            
    context={
        'page': page
    }
    return render(request, 'base/login_register.html',context)

def registerPage(request):
    form = MyUserCreationForm()
    
    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            return redirect("/login")
        else:
            messages.error(request, 'An error occured during registration')
    
    return render(request, 'base/login_register.html',{'form':form})

def logoutUser(request):
    logout(request)
    return redirect('home')
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(Q(topic__name__icontains=q)|
                                Q(name__icontains=q)|
                                Q(description__icontains=q)|
                                Q(host__username__icontains=q))
    topics= Topic.objects.all()
    messages_room = Message.objects.filter(Q(room__topic__name__icontains=q)|
                                           Q(user__username__icontains=q)|
                                           Q(body__icontains=q)) 
    rooms_count = rooms.count()
    
    context={
        'rooms':rooms,
        'topics':topics,
        'rooms_count':rooms_count,
        'messages_room':messages_room
    }
    return render(request, 'base/home.html',context)

def room(request,pk):
    
    room = Room.objects.get(id=pk)
    participants = room.participants.all()
    room_messages = room.message_set.all().order_by('created')
    
    if request.method == 'POST':
        message= Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)
    
    context={
        'room': room,
        'room_messages':room_messages,
        'participants':participants
    }
    
    return render(request,'base/room.html',context)


def userProfile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    messages = user.message_set.all()
    topics = Topic.objects.all()
    context={'user':user,'rooms':rooms,'messages_room':messages,'topics':topics}
    return render(request,'base/profile.html',context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    typeForm = "Create"
    topics = Topic.objects.all()


    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic,created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host = request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')

        )
        form = RoomForm(request.POST)
        return redirect('home')
    context={
        'form':form,
        'topics' : topics,
        'type':typeForm
    }
    
    return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def updateRoom(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    typeForm = "Update"
    
    if request.user != room.host:
        return HttpResponse('You dont have permission to update this Room')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic,created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()

        return redirect('home')
    context={
        'form' : form,
        'type':typeForm,
        'topics':topics,
        'room':room

    }
    return render(request,'base/room_form.html',context)
# Create your views here.
@login_required(login_url='login')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('You are not allow to delete this Room')
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    
    context={
        'obj' : room
    }
    return render(request,'base/delete.html',context)

@login_required(login_url='login')
def deleteMessage(request,pk):
    message = Message.objects.get(id=pk)
    if message.user != request.user:
        return HttpResponse('You are not allow to delete this Message')
    if request.method == 'POST':
        message.delete()
        return redirect('room',pk=message.room.pk)

    context = {'obj' : message}
    return render(request,'base/delete.html',context)

def updateUser(request,pk):
    user = User.objects.get(id= pk)
    form = UserForm(instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk=user.id)
        else:
            messages.error(request, 'An error occured during registration')

    context={
        'user' : user,
        'form' : form

    }
    return render(request,'base/update-user.html',context)


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    topics = Topic.objects.filter(name__icontains=q)
    context={
        'topics': topics
    }
    return render(request,'base/topics.html',context)


def activitiesPage(request):
    
    activities = Message.objects.all()
    context={
        'activities': activities
    }

    return render(request,'base/activities.html',context)