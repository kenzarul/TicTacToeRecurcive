from django.shortcuts import render
from django.http import JsonResponse
from .logic import Game
import numpy as np

def main_menu(request):
    return render(request, 'main_menu.html')

def single_player(request):
    return render(request, 'single_player.html')

def multiplayer(request):
    return render(request, 'multiplayer.html')

def game_board(request):
    difficulty = int(request.GET.get('difficulty', 1))
    request.session['game'] = Game(difficulty).to_dict()

    data = request.session.get('game', None)
    game = Game.from_dict(data)

    context = {
        "some_data": game.board,
    }
    return render(request, 'game_board.html',context)

def make_move(request):
    if request.method == 'POST':
        row = int(request.POST['row'])
        col = int(request.POST['col'])

        game_data = request.session.get('game', None)
        if game_data:
            game = Game.from_dict(game_data)
            if game.make_move(row, col):
                request.session['game'] = game.to_dict()
                return JsonResponse({'success': True, 'game': game.to_dict()})

    return JsonResponse({'success': False})
