from django.urls import path
from . import views

app_name = "game"

urlpatterns = [
    path('', views.main_menu, name='main_menu'),
    path('single/', views.single_player, name='single_player'),
    path('multi/', views.multiplayer, name='multiplayer'),
    path('index/', views.index, name='index'),
    path('<int:pk>/', views.game, name='detail'),
]
