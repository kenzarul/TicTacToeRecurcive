from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect, get_object_or_404

from .forms import NewGameForm, PlayForm
from .models import Game, SubGame

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


@require_http_methods(["GET", "POST"])
def game(request, pk):
    game = get_object_or_404(Game, pk=pk)
    if request.method == "POST":
        # Check for index.
        form = PlayForm(request.POST)
        if form.is_valid():
            print("Playing")
            print(form.cleaned_data)
            game.play(form.cleaned_data['main_index'],
                      form.cleaned_data['sub_index'])
            game.play_auto()
            game.save()
            # Redirect to the same URL so we don't get resubmission warnings.
            # This is a relatively dumb UI; what you would really
            # want to do is have a front-end UI that does requests via
            # AJAX (jQuery or Ember)
            return redirect('game:detail', pk=pk)
        else:
            # What to do? This is a programmer error for now.
            pass

    context = {
        'game': game,
        'active_index': game.active_index,
        'sub_game_0': game.sub_games.filter(index=0).first(),
        'sub_game_1': game.sub_games.filter(index=1).first(),
        'sub_game_2': game.sub_games.filter(index=2).first(),
        'sub_game_3': game.sub_games.filter(index=3).first(),
        'sub_game_4': game.sub_games.filter(index=4).first(),
        'sub_game_5': game.sub_games.filter(index=5).first(),
        'sub_game_6': game.sub_games.filter(index=6).first(),
        'sub_game_7': game.sub_games.filter(index=7).first(),
        'sub_game_8': game.sub_games.filter(index=8).first(),
    }
    return render(request, "game/game_detail_3.html",  context)
