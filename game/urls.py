from django.urls import re_path, path
from . import views

app_name = "game"

urlpatterns = [
    re_path(r'^$', views.main_menu, name='main_menu'),
    re_path(r'^single/$', views.single_player, name='single_player'),
    re_path(r'^multi/$', views.multiplayer, name='multiplayer'),
    re_path(r'^index/$', views.index, name='index'),
    re_path(r'^(?P<pk>\d+)/$', views.game, name='detail'),
    path('', views.test, name='test'),
]