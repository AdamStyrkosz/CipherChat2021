from django.shortcuts import render

# Create your views here.
# chat/views.py
from django.shortcuts import render

def index(request):
    return render(request, 'chat/index.html', {})

def room(request, room_name):
    roomlist = list(room_name)
    listaascii = []
    for letter in roomlist:
        listaascii.append(ord(letter))
    while (len(listaascii) < 16):
        listaascii.append(0)
    key = listaascii[:16]
    return render(request, 'chat/room.html', {
        'key': key,
        'room_name': room_name,
    })