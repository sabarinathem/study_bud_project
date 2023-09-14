from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from .models import Message, Room,Topic,User
from django.db.models import Q
from .forms import RoomForm,UserForm,UserRegisterForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required


# Create your views here.


def login_page(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(email = email)
        except:
            messages.error(request, "User Doesn't Exist")
        user = authenticate(request,email = email,password = password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, "Username OR Password Does't exist") 
        
    context = {'page':page}
    return render(request,'base/login_register.html',context)

def logout_user(request):
    logout(request)
    return redirect('home')

def register_page(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        print(form)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'Error occured during registraction')
    form = UserRegisterForm()
    context = {'form':form}
    return render(request,'base/login_register.html',context)

@login_required(login_url='login')
def home(request):
    # when Search or Click in topic
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    # Rooms
    rooms = Room.objects.filter(
                    Q(topic__name__icontains = q)|
                    Q(name__icontains = q)|
                    Q(description__icontains = q)
                    )
    # Rooms count 
    rooms_count = rooms.count()
    # Topics
    topics = Topic.objects.all()
    # Recent Activities
    room_messages = Message.objects.filter(
                            Q(room__topic__name__icontains = q)|
                            Q(room__name__icontains = q)|
                            Q(room__description__icontains = q)
                            )
    context = {
        'rooms':rooms,
        'topics':topics, 
        'rooms_count':rooms_count, 
        'room_messages':room_messages
        }
    return render(request,'base/home.html',context)

@login_required(login_url='login')
def user_profile(request,pk):
    # user
    user = User.objects.get(id = pk)
    # user created rooms
    rooms = user.room_set.all()
    # Messages sent by user
    room_messages = user.message_set.all()
    # All Topic
    topics = Topic.objects.all()
    context = {
        'user':user,
        'rooms':rooms,
        'room_messages':room_messages,
        'topics':topics
        }
    return render(request,'base/user_profile.html',context)


@login_required(login_url='login')
def update_user(request):
    user = request.user
    if request.method == "POST":
        form = UserForm(request.POST,request.FILES,instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk=user.id)
    form = UserForm(instance=user)
    context = {'form':form}
    return render(request,'base/update_user.html',context)


@login_required(login_url='login')
def room(request,pk):
    # room
    room = Room.objects.get(pk = pk)
    # Peoples who have joined in a room 
    participants = room.participants.all()
    # if the current user does'nt exist in the room then add that user in the room 
    room.participants.add(request.user)
    # code for create message in this room by current user
    if request.method == "POST":
        # message creation by current user 
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )

        return redirect('room',pk = room.id)
    
    # All Messages created in the room
    room_messages = room.message_set.all()
    context = {'room':room,
               'room_messages':room_messages,
               'participants':participants
               }
    return render(request,'base/room.html',context)

@login_required(login_url='login')
def create_room(request):
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        # * if the topic_name is exist in the topic table of name column, then take that (object or row or record) and assign into topic varible, created = False
        # * if the topic name doen't exist in the topic table of name column then (create or insert) topic (object or row or record) and assign the topic object into topic variable , created = True
        topic,created = Topic.objects.get_or_create(name = topic_name)
        # create Room 
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
        return redirect('home')
    # All topics
    topics = Topic.objects.all()
    # Room Create Form
    form = RoomForm()
    context = {
        'form':form,
        'topics':topics,
        'page':'create_room'
        }
    return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def update_room(request,pk):
    page = 'update_room'
    # room
    room = Room.objects.get(id = pk)
    # Room Update Form
    form = RoomForm(instance=room)
    if request.user != room.host:
        return HttpResponse('You cannot update this room because only the host can do this.')

    # Update the room command
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic,created =  Topic.objects.get_or_create(name = topic_name)
        room.topic = topic
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    # All topics 
    topics = Topic.objects.all()
    context = {
        'form':form,
        'topics':topics,
        'room':room,
        'page':page
        }
    return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def delete_room(request,pk):
    # room
    room = Room.objects.get(id = pk)
    # Check the current user == room host
    if request.user != room.host:
        return HttpResponse('You cannot delete this room because only the host can do this.')
    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':'room','room':room})



@login_required(login_url='login')
def delete_message(request,pk):
    # Message
    message = Message.objects.get(id = pk)
    if request.user != message.user:
        return HttpResponse('You cannot delete this message because only the message user can do this.')
    if request.method == "POST":
        message.delete()
        return redirect('room' ,pk = message.room.id)
    return render(request,'base/delete.html',{'obj':'message','message':message})
