from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from game import views

urlpatterns = [
    re_path(r'^$', RedirectView.as_view(url='/game/', permanent=False)),

    # Ton app principale avec namespace
    path('game/', include(('game.urls', 'game'), namespace='game')),

    # Admin
    path('admin/', admin.site.urls),

    # Authentification
    path('accounts/', include('django.contrib.auth.urls')),  # pour login/logout/password
    path('signup/', views.signup, name='signup'),  # vue de création de compte
]
