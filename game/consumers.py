import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
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

        # Get or create game and assign player
        game = await self.get_or_create_game()
        player_assigned = await self.assign_player(game)

        if not player_assigned:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Game is full'
            }))
            await self.close()
            return

        # Send player their assigned mark (X or O)
        await self.send(text_data=json.dumps({
            'type': 'player_assignment',
            'player': player_assigned
        }))

        # ✅ Refresh game from database to get latest state
        game = await self.get_game()

        # Check if two players connected to the room
        if game.player_x and game.player_o:
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
                'type': 'waiting',
                'message': 'Waiting for another player to join'
            }))

    async def disconnect(self, close_code):
        game = await self.get_game()
        if game:
            # If a player disconnects, reset the game
            await database_sync_to_async(self.reset_game)(game)

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def start_game(self, event):
        await self.send(text_data=json.dumps({
            'type': 'start'
        }))

    @database_sync_to_async
    def get_or_create_game(self):
        game, created = Game.objects.get_or_create(room_code=self.room_code)
        return game

    @database_sync_to_async
    def get_game(self):
        return Game.objects.get(room_code=self.room_code)

    @database_sync_to_async
    def assign_player(self, game):
        """
        Assigns the connecting player to either X or O position
        Returns the assigned player mark (X or O) or None if game is full
        """
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
        """
        Reset player assignments when someone disconnects
        """
        if game.player_x == self.channel_name:
            game.player_x = None
        elif game.player_o == self.channel_name:
            game.player_o = None
        game.save()
