import random
import string
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Game, GameHistory
from django.db.models import Q
from django.utils import timezone

from django.http import JsonResponse

from .forms import NewGameForm, PlayForm
from .models import Game


# ======================= Main Menu Views =======================

@login_required
def profile(request):
    sort_order = request.GET.get('sort', 'desc')
    if sort_order == 'asc':
        history_queryset = GameHistory.objects.filter(user=request.user).order_by('date_played')
    else:
        history_queryset = GameHistory.objects.filter(user=request.user).order_by('-date_played')


    seen = set()
    deduped_history = []
    for game in history_queryset:
        key = (
            (game.opponent or '').lower(),
            game.mode,
            game.result,
            game.date_played.strftime('%Y%m%d%H%M'),  # round to minute
            game.game_identifier
        )
        if key not in seen:
            seen.add(key)
            deduped_history.append(game)


    stats = {
        'total': len(deduped_history),
        'wins': sum(1 for g in deduped_history if g.result == 'win'),
        'losses': sum(1 for g in deduped_history if g.result == 'loss'),
        'draws': sum(1 for g in deduped_history if g.result == 'draw'),
    }
    stats['win_rate'] = round((stats['wins'] / stats['total']) * 100, 1) if stats['total'] > 0 else 0

    return render(request, 'game/profile.html', {
        'history': deduped_history,
        'total_games': stats['total'],
        'wins': stats['wins'],
        'losses': stats['losses'],
        'draws': stats['draws'],
        'win_rate': stats['win_rate'],
        'sort_order': sort_order,
    })


def main_menu(request):
    return render(request, 'game/main_menu.html')


def main_menu_guest(request):
    logout(request)
    return render(request, 'game/main_menu.html', {'guest': True})


# ======================= Single Player Views =======================

def how_to_play(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'game/how_to_play.html')
    else:

        return render(request, 'game/how_to_play_full.html')


def single_player(request):
    guest = request.GET.get('guest', None)

    return render(request, 'game/single_player.html', {'guest': guest})


@require_http_methods(["GET", "POST"])
def index(request):
    if request.method == "POST":
        difficulty = request.POST.get("difficulty")
        if difficulty:
            player_x = request.user.username if request.user.is_authenticated else "Guest"
            game = Game.objects.create(
                player_x=player_x,
                player_o=difficulty,  # Use selected difficulty e.g. 'random' or 'minimax'
                board=" " * 9,
                time_x=300,
                time_o=300,
                remaining_x=300,
                remaining_o=300
            )
            game.create_subgames()
            game.play_auto()
            game.save()
            return redirect(game)

        form = NewGameForm(request.POST)
        if form.is_valid():
            player_x = request.user.username if request.user.is_authenticated else "Guest"
            game = Game.objects.create(
                player_x=player_x,
                player_o='random',  # default AI opponent
                board=" " * 9,
                time_x=300,
                time_o=300,
                remaining_x=300,
                remaining_o=300
            )
            game.create_subgames()
            game.play_auto()
            game.save()
            return redirect(game)
    else:
        form = NewGameForm()
    return render(request, 'game/single_player.html', {'form': form})


# ======================= Multiplayer Views =======================

def multiplayer(request):
    return render(request, 'game/multiplayer.html', {
        'time_choices': range(1, 11)
    })


def generate_unique_room_code():
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not Game.objects.filter(room_code=code).exists():
            return code


def create_multiplayer(request):
    if request.method == "POST":
        code = generate_unique_room_code()

        try:
            time_per_player = int(request.POST.get("time", 5))
            if not 1 <= time_per_player <= 10:
                raise ValueError
        except (ValueError, TypeError):
            return render(request, 'game/multiplayer.html', {
                'time_choices': range(1, 11),
                'error': "Invalid time value. Please choose between 1 and 10 minutes."
            })

        game = Game.objects.create(
            room_code=code,
            player_x=None,
            player_o=None,
            board=" " * 9,
            time_x=time_per_player * 60,
            time_o=time_per_player * 60,
        )
        return redirect('game:multiplayer_game', game_id=game.id)

    return redirect('game:multiplayer')


def join_multiplayer(request):
    if request.method == "POST":
        code = request.POST.get('code', '').strip().upper()
        game = Game.objects.filter(room_code=code).first()
        if game and (not game.player_x or not game.player_o):
            return redirect('game:multiplayer_game', game_id=game.id)
        else:
            return render(request, 'game/multiplayer.html', {
                'time_choices': range(1, 11),
                'error': '❌ Invalid code or room is full.'
            })
    return redirect('game:multiplayer')


def multiplayer_game_view(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    return render(request, 'game/multi_player_board.html', {
        'game': game,
        'room_code': game.room_code,
        'my_player': request.user.username if request.user.is_authenticated else "Guest"
    })


# ======================= Classic Game View =======================

@require_http_methods(["GET", "POST"])
def game(request, pk):
    game = get_object_or_404(Game, pk=pk)

    if request.method == "POST" and request.POST.get("surrender") == "1":
        if not game.winner:

            current_username = request.user.username if request.user.is_authenticated else "Guest"
            user_symbol = 'X' if game.player_x == current_username else 'O'
            ai_symbol = 'O' if user_symbol == 'X' else 'X'
            game.winner = ai_symbol
            game.save()

            from django.contrib.auth.models import User
            if request.user.is_authenticated:
                for uname in [game.player_x, game.player_o]:
                    if not uname:
                        continue
                    if uname.lower() in ['random', 'minimax', 'computer']:
                        continue
                    try:
                        user_obj = User.objects.get(username=uname)
                    except User.DoesNotExist:
                        continue
                    symbol = 'X' if uname == game.player_x else 'O'
                    if game.winner in ['draw', ' ']:
                        result = 'draw'
                    elif game.winner == symbol:
                        result = 'win'
                    else:
                        result = 'loss'
                    opponent = game.player_o if uname == game.player_x else game.player_x
                    if opponent and opponent.lower() in ['random', 'minimax', 'computer']:
                        opponent = "Computer"
                    if not GameHistory.objects.filter(
                            user=user_obj,
                            opponent=opponent,
                            mode=('single' if opponent == "Computer" else 'multi'),
                            date_played__gte=game.date_created
                    ).exists():
                        GameHistory.objects.create(
                            user=user_obj,
                            opponent=opponent,
                            mode=('single' if opponent == "Computer" else 'multi'),
                            result=result
                        )

        return redirect('game:detail', pk=pk)

    if request.method == "POST" and not request.POST.get("surrender"):
        form = PlayForm(request.POST)
        if form.is_valid():
            main_index = form.cleaned_data['main_index']
            sub_index = form.cleaned_data['sub_index']

            if not game.winner:
                current_username = request.user.username if request.user.is_authenticated else "Guest"
                player_symbol = 'X' if game.player_x == current_username else 'O'
                try:
                    game.play(main_index, sub_index, player_symbol)
                    game.play_auto()
                except Exception as e:
                    print("Error during move:", e)


            if game.winner:
                from django.contrib.auth.models import User
                for uname in [game.player_x, game.player_o]:
                    if not uname:
                        continue
                    if uname.lower() in ['random', 'minimax', 'computer']:
                        continue
                    try:
                        user_obj = User.objects.get(username=uname)
                    except User.DoesNotExist:
                        continue
                    symbol = 'X' if uname == game.player_x else 'O'
                    if game.winner in ['draw', ' ']:
                        result = 'draw'
                    elif game.winner == symbol:
                        result = 'win'
                    else:
                        result = 'loss'
                    opponent = game.player_o if uname == game.player_x else game.player_x
                    if opponent and opponent.lower() in ['random', 'minimax', 'computer']:
                        opponent = "Computer"
                    if not GameHistory.objects.filter(
                            user=user_obj,
                            opponent=opponent,
                            mode=('single' if opponent == "Computer" else 'multi'),
                            date_played__gte=game.date_created
                    ).exists():
                        GameHistory.objects.create(
                            user=user_obj,
                            opponent=opponent,
                            mode=('single' if opponent == "Computer" else 'multi'),
                            result=result
                        )
            return redirect('game:detail', pk=pk)

    context = {
        'game': game,
        'active_index': game.active_index,
        'last_main_index': game.last_main_index,
        'last_sub_index': game.last_sub_index,
        'sub_game_0': game.sub_games.filter(index=0).first(),
        'sub_game_1': game.sub_games.filter(index=1).first(),
        'sub_game_2': game.sub_games.filter(index=2).first(),
        'sub_game_3': game.sub_games.filter(index=3).first(),
        'sub_game_4': game.sub_games.filter(index=4).first(),
        'sub_game_5': game.sub_games.filter(index=5).first(),
        'sub_game_6': game.sub_games.filter(index=6).first(),
        'sub_game_7': game.sub_games.filter(index=7).first(),
        'sub_game_8': game.sub_games.filter(index=8).first(),
        'next_player': game.next_player,
        'current_user': request.user.username if request.user.is_authenticated else 'Guest',
    }
    return render(request, "game/single_player_board.html", context)


# ======================= Sign Up View =======================

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            password_errors = form.errors.get('password2')
            if password_errors:
                if any('too similar' in str(e) or 'too common' in str(e) for e in password_errors):
                    form.add_error('password2',
                                   "⚠️ Mot de passe trop simple, veuillez choisir un mot de passe plus fort.")
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


def restart_game(request):
    room_code = request.GET.get('room_code')
    try:
        game = Game.objects.get(room_code=room_code)
        game.reset_state()  # Reset the game state
    except Game.DoesNotExist:
        pass
    return redirect('game:multiplayer_game', game_id=game.id)


from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


@csrf_exempt
def register_multiplayer_result(request):

    if request.method == "POST":
        room_code = request.POST.get("room_code")
        winner_symbol = request.POST.get("winner")  # 'X', 'O', or 'draw'
        loser_symbol = request.POST.get("loser")  # 'X', 'O', or 'draw'

        try:
            game = Game.objects.get(room_code=room_code)
            from django.contrib.auth.models import User

            # Get the actual player usernames based on symbols
            if winner_symbol == 'draw':

                for player_username, opponent_username in [(game.player_x, game.player_o),
                                                           (game.player_o, game.player_x)]:
                    if not player_username:
                        continue
                    try:
                        user_obj = User.objects.get(username=player_username)
                        GameHistory.objects.create(
                            user=user_obj,
                            opponent=opponent_username if opponent_username else "Unknown",
                            mode='multi',
                            result='draw',
                            game_identifier=room_code  # Use room_code as unique identifier
                        )
                    except User.DoesNotExist:
                        continue
            else:
                # Handle win/loss case
                # Map symbols to actual usernames
                winner_username = game.player_x if winner_symbol == 'X' else game.player_o
                loser_username = game.player_o if winner_symbol == 'X' else game.player_x

                # Create records for both winner and loser
                for username, result, opponent in [
                    (winner_username, 'win', loser_username),
                    (loser_username, 'loss', winner_username)
                ]:
                    if not username:
                        continue
                    try:
                        user_obj = User.objects.get(username=username)
                        GameHistory.objects.create(
                            user=user_obj,
                            opponent=opponent if opponent else "Unknown",
                            mode='multi',
                            result=result,
                            game_identifier=room_code  # Use room_code as unique identifier
                        )
                    except User.DoesNotExist:
                        continue

            return HttpResponse("OK")
        except Exception as e:
            return HttpResponse(f"Error: {e}", status=400)
    return HttpResponse("Invalid method", status=405)

