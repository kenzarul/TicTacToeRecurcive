import json
from channels.generic.websocket import AsyncWebsocketConsumer

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.room_group_name = f"game_{self.game_id}"

        # Add this connection to the group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        move = data["move"]
        player = data["player"]

        # Broadcast the move to all players in the game
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "game_move",
                "move": move,
                "player": player,
            }
        )

    async def game_move(self, event):
        await self.send(text_data=json.dumps({
            "move": event["move"],
            "player": event["player"],
        }))
