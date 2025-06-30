from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "game"

urlpatterns = [
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='game:main_menu'), name='logout'),
    # Main menus
    path('', views.main_menu, name='main_menu'),
    path('guest/', views.main_menu_guest, name='main_menu_guest'),
    path('how-to-play/', views.how_to_play, name='how_to_play'),

    # Single player
    path('single/', views.single_player, name='single_player'),
    path('index/', views.index, name='index'),
    path('profile/', views.profile, name='profile'),
    path("profile/", views.user_profile, name="profile"),

    # Classic game view
    path('<int:pk>/', views.game, name='detail'),

    # Multiplayer
    path('multi/', views.multiplayer, name='multiplayer'),  # Multiplayer lobby page
    path('multi/create/', views.create_multiplayer, name='create_multiplayer'),  # Create room
    path('multi/join/', views.join_multiplayer, name='join_multiplayer'),  # Join room
    path('multi/game/<int:game_id>/', views.multiplayer_game_view, name='multiplayer_game'),  # Multiplayer game page

]
