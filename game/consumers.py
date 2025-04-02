import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Game, SubGame

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle new player connections."""
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.room_group_name = f'game_{self.game_id}'

        # Join the game room
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Handle player disconnections."""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Receive moves from players and update the game."""
        data = json.loads(text_data)
        game_id = data['game_id']
        main_index = int(data['main_index'])
        sub_index = int(data['sub_index'])
        player = data['player']

        game = Game.objects.get(pk=game_id)

        # Validate turn
        if game.next_player != player:
            return

        # Try to play the move
        try:
            game.play(main_index, sub_index)
            game.save()

            # Broadcast move to all players
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "game_update",
                    "game_id": game_id,
                    "main_index": main_index,
                    "sub_index": sub_index,
                    "player": player,
                    "board": game.board,
                    "winner": game.is_game_over
                }
            )
        except Exception as e:
            print(f"Move error: {e}")

    async def game_update(self, event):
        """Send game updates to all connected clients."""
        await self.send(text_data=json.dumps(event))
