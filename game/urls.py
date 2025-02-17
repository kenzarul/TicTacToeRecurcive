from django.urls import re_path
from . import views

app_name = "game"  # ✅ Add this line

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^(?P<pk>\d+)/$', views.game, name='detail'),
]
