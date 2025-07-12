import json
import asyncio
import aiohttp
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Game

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
        if game.player_x and game.player_o:
            if not await self.subgames_exist(game):
                await self.create_subgames(game)
                await self.start_timer_loop()
            game_data = await self.get_game_data()
            # BEGIN CHANGES: Send "start_game" message to all group members instead of a single send.
            await self.channel_layer.group_send(self.group_name, {
                'type': 'start_game',
                'next_player': game_data['next_player'],
                'player_x': game_data['player_x'],
                'player_o': game_data['player_o'],
                'time_x': game_data['remaining_x'],
                'time_o': game_data['remaining_o'],
            })
            # END CHANGES
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
        # Removed resetting player assignment to allow re-connection for room creator.

    async def start_game(self, event):
        game_data = await self.get_game_data()
        current_user = self.scope["user"].username if self.scope["user"].is_authenticated else "Guest"
        if current_user == game_data['player_x']:
            my_player = game_data['player_x']
            opponent = game_data['player_o'] or "Waiting..."
        else:
            my_player = game_data['player_o']
            opponent = game_data['player_x'] or "Waiting..."
        await self.send(text_data=json.dumps({
            'type': 'start',
            'next_player': game_data['next_player'],
            'my_player': my_player,
            'opponent': opponent,
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
                'winning_line': list(winning_line) if winning_line else None,
            }
        )

        # Replace the HTTP request approach with our direct database call
        if game_data['winner']:
            await self.record_game_result(game, game_data['winner'])

        if not game_data['winner']:
            await self.start_timer_loop()

    async def handle_surrender(self, data):
        surrendering_player = data.get('player')
        winner = 'O' if surrendering_player == 'X' else 'X'
        # --- Set the winner in the database immediately and save ---
        game = await self.get_game()
        if game:
            await self.set_game_winner(game, winner)
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'surrender_game',
                'winner': winner,
                'message': f"{surrendering_player} surrendered. {winner} wins!",
            }
        )

        # Replace HTTP request with direct database call
        if game:
            await self.record_game_result(game, winner)

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

    async def handle_restart(self):
        """
        Handle the restart action by resetting the game state and notifying all players.
        """
        game = await self.get_game()
        if game:
            await self.reset_full_game()  # Reset game state in the database (calls game.reset_state())
            # Reset internal vote tracking
            self.vote_yes = {'X': False, 'O': False}
            self.vote_no = {'X': False, 'O': False}
            # Fetch fresh game data after reset
            game_data = await self.get_game_data()
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'restart_game',
                    'next_player': game_data['next_player'],
                    'player_x': game_data['player_x'],
                    'player_o': game_data['player_o'],
                    'time_x': game_data['remaining_x'],
                    'time_o': game_data['remaining_o'],
                }
            )
            await self.start_timer_loop()

    async def restart_game(self, event):
        """
        Notify the frontend with complete game reset data.
        """
        await self.send(text_data=json.dumps({
            'type': 'restart',
            'next_player': event.get('next_player'),
            'player_x': event.get('player_x'),
            'player_o': event.get('player_o'),
            'time_x': event.get('time_x'),
            'time_o': event.get('time_o'),
        }))

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

    async def update_timers(self, event):
        # Handler for "update_timers" messages
        await self.send(text_data=json.dumps({
            'type': 'timer_update',
            'time_x': event.get('time_x'),
            'time_o': event.get('time_o'),
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
        # If user is authenticated, check if already assigned.
        if self.scope["user"].is_authenticated:
            username = self.scope["user"].username
            if game.player_x == username:
                return 'X'
            elif game.player_o == username:
                return 'O'
        else:
            # For anonymous users, we can use a similar check based on a session id or unique identifier.
            # Here we simply check if either guest slot is already filled with any guest value.
            # In a real app, you might store guest IDs in the session.
            pass  # ...existing logic for non-authenticated users...

        # Assign new player if not already assigned.
        if not game.player_x:
            user_id = self.scope["user"].username if self.scope["user"].is_authenticated else "Guest_1"
            game.player_x = user_id
            game.save()
            return 'X'
        elif not game.player_o:
            user_id = self.scope["user"].username if self.scope["user"].is_authenticated else "Guest_2"
            game.player_o = user_id
            game.save()
            return 'O'
        # If both players are already assigned, reassign if the connecting user matches an existing one.
        if self.scope["user"].is_authenticated:
            if game.player_x == self.scope["user"].username:
                return 'X'
            elif game.player_o == self.scope["user"].username:
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
        sub_game = game.sub_games.filter(index=main_index).first()
        if not sub_game:
            raise ValueError("SubGame does not exist")
        # Unpack winner and winning_line from sub_game.play
        winner, winning_line = sub_game.play(sub_index, symbol)
        game.last_main_index = main_index
        game.last_sub_index = sub_index
        game.last_player = symbol
        if winner:
            game.board = game.board[:main_index] + winner + game.board[main_index + 1:]
        elif ' ' not in sub_game.board:
            game.board = game.board[:main_index] + ' ' + game.board[main_index + 1:]
        game.set_active_index(sub_index)
        game.save()
        game.is_game_over  # Trigger win check
        return (winner, winning_line)

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

    @database_sync_to_async
    def set_game_winner(self, game, winner):
        game.winner = winner
        game.save()

    # Add new utility method for recording game results directly
    @database_sync_to_async
    def record_game_result(self, game, winner):
        """
        Record game result for both players in GameHistory with improved deduplication
        """
        from django.contrib.auth.models import User
        from .models import GameHistory
        import time
        import random
        from django.db import transaction
        from django.utils import timezone
        from datetime import timedelta

        # Try to get both user objects
        player_x_obj = None
        player_o_obj = None

        if game.player_x:
            try:
                player_x_obj = User.objects.get(username=game.player_x)
            except User.DoesNotExist:
                pass

        if game.player_o:
            try:
                player_o_obj = User.objects.get(username=game.player_o)
            except User.DoesNotExist:
                pass

        # Skip if neither player is a registered user
        if not player_x_obj and not player_o_obj:
            return

        # Get exact timestamp for this game result - more precise than int(time.time())
        now = timezone.now()
        time_str = now.strftime("%Y%m%d%H%M%S%f")

        # Create a precise game identifier that includes timestamp to microsecond precision
        precise_game_id = f"{game.room_code}_{time_str}"

        # Map players to their symbols and results
        player_results = {}

        # Record which player is X and which is O
        if player_x_obj:
            player_results[player_x_obj.username] = {"symbol": "X", "user_obj": player_x_obj}
        if player_o_obj:
            player_results[player_o_obj.username] = {"symbol": "O", "user_obj": player_o_obj}

        # Determine result for each player based on winner
        if winner == 'draw':
            for username in player_results:
                player_results[username]["result"] = 'draw'
        else:
            # Winner gets 'win', other player gets 'loss'
            for username, data in player_results.items():
                if data["symbol"] == winner:
                    player_results[username]["result"] = 'win'
                else:
                    player_results[username]["result"] = 'loss'

        # Use a transaction to ensure atomicity
        with transaction.atomic():
            # Look for any recent records (within last minute) with same result to avoid duplicates
            recent_time = now - timedelta(minutes=1)

            # Create history entries for each player
            for username, data in player_results.items():
                opponent_username = game.player_o if username == game.player_x else game.player_x

                # Check for recent entries with same characteristics
                existing_records = GameHistory.objects.filter(
                    user=data["user_obj"],
                    opponent=opponent_username,
                    mode='multi',
                    result=data["result"],
                    date_played__gte=recent_time
                )

                # Only create if no matching recent record exists
                if not existing_records.exists():
                    GameHistory.objects.create(
                        user=data["user_obj"],
                        opponent=opponent_username or "Unknown",
                        mode='multi',
                        result=data["result"],
                        game_identifier=precise_game_id
                    )
                    print(f"Created game history: {username} vs {opponent_username}, Result: {data['result']}, Game ID: {precise_game_id}")
                else:
                    print(f"Skipped duplicate game history for: {username} vs {opponent_username}, Game ID: {precise_game_id}")
