import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Game


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope['url_route']['kwargs']['room_code']
        self.group_name = f"game_{self.room_code}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        game = await self.get_or_create_game()
        player_assigned = await self.assign_player(game)

        if not player_assigned:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Game is full'
            }))
            await self.close()
            return

        await self.send(text_data=json.dumps({
            'type': 'player_assignment',
            'player': player_assigned
        }))

        game = await self.get_game()
        if game.player_x and game.player_o:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'start_game',
                }
            )
        else:
            await self.send(text_data=json.dumps({
                'type': 'waiting',
                'message': 'Waiting for another player to join'
            }))

    async def disconnect(self, close_code):
        game = await self.get_game()
        if game:
            await self.reset_game(game)

        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def start_game(self, event):
        game_data = await self.get_game_data()
        await self.send(text_data=json.dumps({
            'type': 'start',
            'next_player': game_data['next_player'],
            'player_x': game_data['player_x'],
            'player_o': game_data['player_o'],
        }))

    async def receive(self, text_data):
        data = json.loads(text_data)
        main_index = data.get('main_index')
        sub_index = data.get('sub_index')
        player = data.get('player')

        game = await self.get_game()
        if not game:
            return

        try:
            winner = await self.play_move(game, main_index, sub_index)
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
            return

        game_data = await self.get_game_data()

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'move',
                'main_index': main_index,
                'sub_index': sub_index,
                'player': player,
                'next_player': game_data['next_player'],
                'winner': game_data['winner'],
                'active_index': game_data['active_index'],
            }
        )

    async def move(self, event):
        await self.send(text_data=json.dumps({
            'type': 'move',
            'main_index': event['main_index'],
            'sub_index': event['sub_index'],
            'player': event['player'],
            'next_player': event['next_player'],
            'winner': event['winner'],
            'active_index': event['active_index'],
        }))

    # ----------------------------
    # Database Helpers (Thread-safe)
    # ----------------------------

    @database_sync_to_async
    def get_or_create_game(self):
        game, _ = Game.objects.get_or_create(room_code=self.room_code)
        return game

    @database_sync_to_async
    def get_game(self):
        try:
            return Game.objects.get(room_code=self.room_code)
        except Game.DoesNotExist:
            return None

    @database_sync_to_async
    def get_game_data(self):
        game = Game.objects.get(room_code=self.room_code)
        return {
            'next_player': game.next_player,
            'player_x': game.player_x,
            'player_o': game.player_o,
            'winner': game.winner,
            'active_index': game.active_index,
        }

    @database_sync_to_async
    def assign_player(self, game):
        if not game.player_x:
            game.player_x = self.channel_name
            game.save()
            return 'X'
        elif not game.player_o:
            game.player_o = self.channel_name
            game.save()
            return 'O'
        return None

    @database_sync_to_async
    def reset_game(self, game):
        if game.player_x == self.channel_name:
            game.player_x = None
        elif game.player_o == self.channel_name:
            game.player_o = None
        game.save()

    @database_sync_to_async
    def play_move(self, game, main_index, sub_index):
        return game.play(main_index, sub_index)
