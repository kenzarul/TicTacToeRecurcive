from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect, get_object_or_404
from .forms import NewGameForm, PlayForm
from .models import Game, SubGame
from django.shortcuts import render, redirect
from django.http import JsonResponse
import string
import random


def main_menu(request):
    return render(request, 'game/main_menu.html')

def single_player(request):
    return render(request, 'game/single_player.html')

def multiplayer(request):
    return render(request, 'game/multiplayer.html')

@require_http_methods(["GET", "POST"])
def index(request):
    if request.method == "POST":
        form = NewGameForm(request.POST)
        # Theoretically the only way this form can be invalid
        # is in the case of programmer error or malfeasance --
        # the user doesn't have anything to do.
        if form.is_valid():
            game = form.create()
            # In case the computer is X, it goes first.
            game.play_auto()
            game.save()
            return redirect(game)
    else:
        form = NewGameForm()
    return render(request, 'game/single_player.html', {'form': form})

def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def join_room(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        code = data.get("code")

        # Check if the room exists
        game = Game.objects.filter(id=code).first()
        if game:
            return JsonResponse({"success": True, "redirect_url": f"/game/{game.id}/"})  # Redirect to room
        return JsonResponse({"success": False})

    return JsonResponse({"error": "Invalid request"}, status=400)

def board_view(request):
    return render(request, "game/board.html")  # Ensure board.html exists


@require_http_methods(["GET", "POST"])
def game(request, pk):
    game = get_object_or_404(Game, pk=pk)
    if request.method == "POST":
        form = PlayForm(request.POST)
        if form.is_valid():
            game.play(form.cleaned_data['main_index'],
                      form.cleaned_data['sub_index'])
            game.play_auto()
            game.save()
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
        'next_player': game.next_player
    }
    return render(request, "game/game_detail_3.html", context)