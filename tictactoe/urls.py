from django.urls import include, path, re_path
from django.views.generic import RedirectView
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    re_path(r'^$', RedirectView.as_view(url='/game/', permanent=False)),
    path('game/', include('game.urls', namespace='game')),
    path('admin/', admin.site.urls),
    path('', include ('game.urls', namespace='game')),
]