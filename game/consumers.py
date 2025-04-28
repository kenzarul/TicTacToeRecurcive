# game/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Game

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope['url_route']['kwargs']['room_code']
        self.group_name = f"game_{self.room_code}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

        # Check if two players connected to the room
        game = await self.get_game()

        if game and game.player_x and game.player_o:
            # Send start signal to both players
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'start_game',
                }
            )
        else:
            # Only one player, still waiting
            await self.send(text_data=json.dumps({
                'type': 'waiting'
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        main_index = data['main_index']
        sub_index = data['sub_index']
        player = data['player']

        game = await self.get_game()

        if not game:
            await self.send(text_data=json.dumps({'error': 'Game not found.'}))
            return

        if game.winner:
            await self.send(text_data=json.dumps({'error': 'Game already over.'}))
            return

        if player != (game.player_x if game.next_player == 'X' else game.player_o):
            await self.send(text_data=json.dumps({'error': 'Not your turn.'}))
            return

        winner = game.play(main_index, sub_index)

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'game_update',
                'main_index': main_index,
                'sub_index': sub_index,
                'player': 'X' if game.next_player == 'O' else 'O',  # previous move
                'next_player': game.next_player,
                'winner': winner
            }
        )

    async def start_game(self, event):
        # Send "start" signal to all
        await self.send(text_data=json.dumps({
            'type': 'start'
        }))

    async def game_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'move',
            'main_index': event['main_index'],
            'sub_index': event['sub_index'],
            'player': event['player'],
            'next_player': event['next_player'],
            'winner': event['winner']
        }))

    async def get_game(self):
        try:
            return await database_sync_to_async(Game.objects.get)(room_code=self.room_code)
        except Game.DoesNotExist:
            return None

from channels.db import database_sync_to_async
