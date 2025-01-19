from django.shortcuts import render

def main_menu(request):
    return render(request, 'main_menu.html')

def single_player(request):
    return render(request, 'single_player.html')

def multiplayer(request):
    return render(request, 'multiplayer.html')

def game_board(request):
    # Placeholder for the game board logic
    return render(request, 'game_board.html')
# Create your views here.
