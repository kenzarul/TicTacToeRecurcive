from django.urls import path
from . import views

app_name = "game"

urlpatterns = [
    # Main menus
    path('', views.main_menu, name='main_menu'),
    path('guest/', views.main_menu_guest, name='main_menu_guest'),

    # Single player
    path('single/', views.single_player, name='single_player'),
    path('index/', views.index, name='index'),

    # Classic game view
    path('<int:pk>/', views.game, name='detail'),

    # Multiplayer
    path('multi/', views.multiplayer, name='multiplayer'),  # Multiplayer lobby page
    path('multi/create/', views.create_multiplayer, name='create_multiplayer'),  # Create room
    path('multi/join/', views.join_multiplayer, name='join_multiplayer'),  # Join room
    path('multi/game/<int:game_id>/', views.multiplayer_game_view, name='multiplayer_game'),  # Multiplayer game page
]
