from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from game import views
from django.http import HttpResponse

def healthz(request): 
    return HttpResponse("OK")

def health(request):
    return HttpResponse("OK")


urlpatterns = [
    path("healthz/", healthz),
    path("health/", health),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='game:main_menu'), name='logout'),
    path('', RedirectView.as_view(pattern_name='game:main_menu', permanent=False)),  # Redirect to main_menu
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # login/logout
    path('signup/', views.signup, name='signup'),  # Laisse comme ça si tu utilises directement `views.signup`

    path('game/', include(('game.urls', 'game'), namespace='game')),  # ton app
    path('guest/', views.main_menu_guest, name='main_menu_guest'),

    path('restart/', views.restart_game, name='restart_game'),
]

# Serve media files in development and production (handled by nginx in production)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
