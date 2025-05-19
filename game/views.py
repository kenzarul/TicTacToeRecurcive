from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
import random
import string
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from game.models import Game
from django.contrib.auth import logout

from .forms import NewGameForm, PlayForm
from .models import Game, SubGame
from django.db.models import Q

# ======================= Main Menu Views =======================
@login_required
def profile(request):
    user_games = Game.objects.filter(
        Q(player_x=request.user) | Q(player_o=request.user)
    )
    return render(request, 'game/profile.html', {'user_games': user_games})
@login_required
def main_menu(request):
    return render(request, 'game/main_menu.html')

def main_menu_guest(request):
    logout(request)
    return render(request, 'game/main_menu.html', {'guest': True})

# ======================= Single Player Views =======================
def how_to_play(request):
    return render(request, 'game/how_to_play.html')
# ======================= Single Player Views =======================

def single_player(request):
    return render(request, 'game/single_player.html')

def multiplayer(request):
    return render(request, 'game/multiplayer.html')
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
                    form.add_error('password2', "⚠️ Mot de passe trop simple, veuillez choisir un mot de passe plus fort.")
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@require_http_methods(["GET", "POST"])
def index(request):
    if request.method == "POST":
        form = NewGameForm(request.POST)
        if form.is_valid():
            game = form.create()
            game.play_auto()
            game.save()
            return redirect(game)
    else:
        form = NewGameForm()
    return render(request, 'game/single_player.html', {'form': form})

# ======================= Multiplayer Lobby View =======================

def multiplayer(request):
    return render(request, 'game/multiplayer.html')

# ======================= Multiplayer Game View =======================

from django.shortcuts import render, get_object_or_404

def multiplayer_game_view(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    return render(request, 'game/test.html', {
        'game': game,
        'my_player': request.user.username if request.user.is_authenticated else "Guest"
    })



# ======================= Multiplayer Create/Join Room Views =======================

def generate_unique_room_code():
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not Game.objects.filter(room_code=code).exists():
            return code

def create_multiplayer(request):
    if request.method == "POST":
        code = generate_unique_room_code()
        game = Game.objects.create(
            player_x=None,  # Let WebSocket assign
            player_o=None,
            board=" " * 9,
            room_code=code
        )
        return redirect('game:multiplayer_game', game_id=game.id)
    return redirect('game:multiplayer')
def join_multiplayer(request):
    if request.method == "POST":
        code = request.POST.get('code', '').strip().upper()
        game = Game.objects.filter(room_code=code, player_o__isnull=True).first()

        if game:
            return redirect('game:multiplayer_game', game_id=game.id)
        else:
            return render(request, 'game/multiplayer.html', {'error': '❌ Invalid code or room is full.'})

    return redirect('game:multiplayer')


# ======================= Classic Single Game Play View =======================

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

# ======================= Authentication View =======================

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('game:main_menu')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
