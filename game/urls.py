from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_menu, name='main_menu'),
    path('single-player/', views.single_player, name='single_player'),
    path('multiplayer/', views.multiplayer, name='multiplayer'),
    path('game-board/', views.game_board, name='game_board'),
]
