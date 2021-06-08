import json
from channels.generic.websocket import WebsocketConsumer

import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Message



class ChatConsumer(WebsocketConsumer):
    #funkcja pobierająca wiadomości z bazy danych (wszystkie wiadomości z danego pokoju), wysyłająca tylko do JEDENGO UŻYTKOWNIKA, który wywołał zapytanie
    def fetch_messages(self,data):
        room = data['room'];
        messages = Message.last_10_messages(self,room)
        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        }
        print(content)
        self.send_message(content)

    #funcja odczytująca wiadomość od klienta, zapisuje ją do bazy danych w formie zaszyfrowanej, następnie wysyła do WSZYSTKICH UŻYTKOWNIKÓW
    def new_message(self,data):
        author = data['room']
        message = Message.objects.create(author=author,content=data['message'])
        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }
        print(content)
        return self.send_chat_message(content)

    #tworzenie tablicy wiadomości w formacie json
    def messages_to_json(self,messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result
    #zamiana jednej wiadomości na format json
    def message_to_json(self,message):
        return {
            'author': message.author,
            'content': message.content,
            'timestap': str(message.timestamp)
        }

    #tablica komend, powiązanie komendy z jsona z nazwa fukcji
    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message,
    }

    #czynności wykonywane przy podłączeniu nowego użytkownika
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        content = {
            'command': 'counter',
            'message': 1
        }
        self.send_chat_message(content)

    # czynności wykonywane przy odłączniu nowego użytkownika
    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        content = {
            'command': 'counter',
            'message': -1
        }
        self.send_chat_message(content)

   # czynności wykonywane podczas otrzymania wiadomości z WebSocketu
    def receive(self, text_data):
        data = json.loads(text_data)
        print(data)
        self.commands[data['command']](self,data)  #przypisanie nazwy komendy do nazwy fukcji (porownanie)

    #funcka rozpoczynająca wysłanie wiadomości do całej grupy, nadaje typ i wywołuje odpowiednią funkcje
    def send_chat_message(self,message):
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message', # --> nazwa FUNKCJI ktora wysyla wiadomosc
                'message': message
            }
        )

    #wysla wiadomosc do jednego odbiorcy
    def send_message(self,message):
        self.send(text_data=json.dumps(message))

    #obsluguje event wyslania wiadomosci do calej grupy
    def chat_message(self,event):
        message = event['message']
        self.send(text_data=json.dumps(message))


