import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.exceptions import ValidationError
from .models import Game

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.room_group_name = f'game_{self.game_id}'

        # Join game group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave game group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        main_index = data['main_index']
        sub_index = data['sub_index']
        player = data['player']

        try:
            game = Game.objects.get(pk=self.game_id)

            if game.winner:
                await self.send(text_data=json.dumps({
                    'error': 'Game already over.',
                    'winner': game.winner,
                }))
                return

            # Figure out if player is X or O
            if player == game.player_x:
                player_symbol = 'X'
            elif player == game.player_o:
                player_symbol = 'O'
            else:
                await self.send(text_data=json.dumps({
                    'error': 'Invalid player.'
                }))
                return

            # Check turn
            if player_symbol != game.next_player:
                await self.send(text_data=json.dumps({
                    'error': 'Not your turn.'
                }))
                return

            winner = game.play(main_index, sub_index)

            # Broadcast move to everyone
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'move_message',
                    'main_index': main_index,
                    'sub_index': sub_index,
                    'player': player_symbol,
                    'next_player': 'O' if player_symbol == 'X' else 'X',
                    'winner': winner
                }
            )

        except Game.DoesNotExist:
            await self.send(text_data=json.dumps({
                'error': 'Game not found.'
            }))
        except (ValidationError, ValueError, IndexError) as e:
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))

    async def move_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'move',
            'main_index': event['main_index'],
            'sub_index': event['sub_index'],
            'player': event['player'],
            'next_player': event['next_player'],
            'winner': event['winner'],
        }))
