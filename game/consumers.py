import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Game
from .models import GameHistory
def record_game_result(winner, player_x, player_o):
    if winner == "X":
        GameHistory.objects.create(user=player_x, result="win")
        GameHistory.objects.create(user=player_o, result="loss")
    elif winner == "O":
        GameHistory.objects.create(user=player_o, result="win")
        GameHistory.objects.create(user=player_x, result="loss")
    else:
        GameHistory.objects.create(user=player_x, result="draw")
        GameHistory.objects.create(user=player_o, result="draw")

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope['url_route']['kwargs']['room_code']
        self.group_name = f"game_{self.room_code}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        self.timer_task = None
        self.vote_yes = {'X': False, 'O': False}
        self.vote_no = {'X': False, 'O': False}

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
        if game.player_x and game.player_o and not await self.subgames_exist(game):
            await self.create_subgames(game)
            await self.channel_layer.group_send(self.group_name, {'type': 'start_game'})
            await self.start_timer_loop()
        else:
            await self.send(text_data=json.dumps({
                'type': 'waiting',
                'message': 'Waiting for another player to join'
            }))

    async def disconnect(self, close_code):
        game = await self.get_game()
        if game:
            await self.reset_game(game)
        if self.timer_task:
            self.timer_task.cancel()
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def start_game(self, event):
        game_data = await self.get_game_data()
        await self.send(text_data=json.dumps({
            'type': 'start',
            'next_player': game_data['next_player'],
            'player_x': game_data['player_x'],
            'player_o': game_data['player_o'],
            'time_x': game_data['remaining_x'],  # Send correct remaining time for X
            'time_o': game_data['remaining_o'],  # Send correct remaining time for O
        }))

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'move':
            await self.handle_move(data)
        elif action == 'surrender':
            await self.handle_surrender(data)
        elif action == 'replay_vote':
            await self.handle_vote(data)
        elif action == 'restart_game':
            await self.handle_restart()

    async def handle_move(self, data):
        main_index = data.get('main_index')
        sub_index = data.get('sub_index')
        player = data.get('player')

        game = await self.get_game()
        if not game or game.winner:
            return

        subgame = await self.get_subgame_by_index(game, main_index)
        if subgame and subgame.winner:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f"Subgrid {main_index} has already been won by {subgame.winner}."
            }))
            return

        try:
            # --- CHANGED: get both winner and winning_line from play_move ---
            winner, winning_line = await self.play_move(game, main_index, sub_index, player)
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
                'time_x': game_data['time_x'],
                'time_o': game_data['time_o'],
                'winning_line': list(winning_line) if winning_line else None,  # <-- send winning_line
            }
        )

        if not game_data['winner']:
            await self.start_timer_loop()

    async def handle_surrender(self, data):
        surrendering_player = data.get('player')
        winner = 'O' if surrendering_player == 'X' else 'X'
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'surrender_game',
                'winner': winner,
                'message': f"{surrendering_player} surrendered. {winner} wins!",
            }
        )
        # Do NOT reset the game state here. Wait for replay votes.

    async def handle_vote(self, data):
        player = data.get('from')
        vote = data.get('vote')

        if vote == 'yes':
            self.vote_yes[player] = True
        else:
            self.vote_no[player] = True

        await self.channel_layer.group_send(self.group_name, {
            'type': 'replay_vote',
            'from': player,
            'vote': vote,
        })

        if self.vote_yes['X'] and self.vote_yes['O']:
            await self.reset_full_game()
            self.vote_yes = {'X': False, 'O': False}
            self.vote_no = {'X': False, 'O': False}
            await self.channel_layer.group_send(self.group_name, {'type': 'restart_game'})
        elif self.vote_no['X'] or self.vote_no['O']:
            self.vote_yes = {'X': False, 'O': False}
            self.vote_no = {'X': False, 'O': False}

    async def restart_game(self, event):
        await self.send(text_data=json.dumps({
            'type': 'restart'
        }))
        await self.start_timer_loop()

    async def start_timer_loop(self):
        if self.timer_task:
            self.timer_task.cancel()

        async def countdown():
            while True:
                await asyncio.sleep(1)
                game = await self.get_game()
                if not game or game.winner:
                    break

                current = game.next_player
                await self.decrease_timer(game, current)

                game_data = await self.get_game_data()
                await self.channel_layer.group_send(self.group_name, {
                    'type': 'update_timers',
                    'time_x': game_data['remaining_x'],  # Send updated time for X
                    'time_o': game_data['remaining_o'],  # Send updated time for O
                })

                if game_data['remaining_x'] <= 0:
                    await self.channel_layer.group_send(self.group_name, {
                        'type': 'surrender_game',
                        'winner': 'O',
                        'message': '⏰ X ran out of time. O wins!',
                    })
                    break
                if game_data['remaining_o'] <= 0:
                    await self.channel_layer.group_send(self.group_name, {
                        'type': 'surrender_game',
                        'winner': 'X',
                        'message': '⏰ O ran out of time. X wins!',
                    })
                    break

        self.timer_task = asyncio.create_task(countdown())

    async def move(self, event):
        await self.send(text_data=json.dumps({
            'type': 'move',
            'main_index': event['main_index'],
            'sub_index': event['sub_index'],
            'player': event['player'],
            'next_player': event['next_player'],
            'winner': event['winner'],
            'active_index': event['active_index'],
            'time_x': event['time_x'],
            'time_o': event['time_o'],
            'winning_line': event.get('winning_line'),  # <-- pass through
        }))

    async def surrender_game(self, event):
        await self.send(text_data=json.dumps({
            'type': 'surrender',
            'winner': event['winner'],
            'message': event['message'],
        }))
        if self.timer_task:
            self.timer_task.cancel()

    async def replay_vote(self, event):
        await self.send(text_data=json.dumps({
            'type': 'replay_vote',
            'from': event['from'],
            'vote': event['vote'],
        }))

    async def restart_game(self, event):
        await self.send(text_data=json.dumps({
            'type': 'restart'
        }))

    async def update_timers(self, event):
        await self.send(text_data=json.dumps({
            'type': 'timer_update',
            'time_x': event['time_x'],
            'time_o': event['time_o'],
        }))

    # ---------------------------- Database Helpers ----------------------------

    @database_sync_to_async
    def get_or_create_game(self):
        return Game.objects.get_or_create(room_code=self.room_code)[0]

    @database_sync_to_async
    def get_game(self):
        try:
            return Game.objects.get(room_code=self.room_code)
        except Game.DoesNotExist:
            return None

    @database_sync_to_async
    def get_subgame_by_index(self, game, main_index):
        return game.sub_games.filter(index=main_index).first()

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
    def play_move(self, game, main_index, sub_index, symbol=None):
        # --- CHANGED: return both winner and winning_line from SubGame.play ---
        sub_game = game.sub_games.filter(index=main_index).first()
        if not sub_game:
            raise ValueError("SubGame does not exist")
        result = sub_game.play(sub_index, symbol)
        # result is (winner, winning_line)
        game.last_main_index = main_index
        game.last_sub_index = sub_index
        game.last_player = symbol
        if result[0]:
            game.board = game.board[:main_index] + result[0] + game.board[main_index + 1:]
        elif ' ' not in sub_game.board:
            game.board = game.board[:main_index] + ' ' + game.board[main_index + 1:]
        game.set_active_index(sub_index)
        game.save()
        game.is_game_over  # Trigger win check
        return result

    @database_sync_to_async
    def get_game_data(self):
        game = Game.objects.get(room_code=self.room_code)
        return {
            'next_player': game.next_player,
            'player_x': game.player_x,
            'player_o': game.player_o,
            'winner': game.winner,
            'active_index': game.active_index,
            'time_x': game.time_x,
            'time_o': game.time_o,
            'remaining_x': game.remaining_x,
            'remaining_o': game.remaining_o,
        }

    @database_sync_to_async
    def decrease_timer(self, game, player):
        if player == 'X' and game.remaining_x > 0:
            game.remaining_x -= 1
        elif player == 'O' and game.remaining_o > 0:
            game.remaining_o -= 1
        game.save()

    @database_sync_to_async
    def subgames_exist(self, game):
        return game.sub_games.exists()

    @database_sync_to_async
    def create_subgames(self, game):
        game.create_subgames()

    @database_sync_to_async
    def reset_full_game(self):
        game = Game.objects.get(room_code=self.room_code)
        game.reset_state()
        game.save()