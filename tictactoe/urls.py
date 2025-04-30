from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from game import views

urlpatterns = [
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='game:main_menu'), name='logout'),
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # login/logout
    path('signup/', views.signup, name='signup'),  # Laisse comme ça si tu utilises directement `views.signup`

    path('game/', include(('game.urls', 'game'), namespace='game')),  # ton app
    path('guest/', views.main_menu_guest, name='main_menu_guest'),

]
