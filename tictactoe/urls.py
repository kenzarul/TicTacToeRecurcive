from django.urls import include, path
from django.views.generic import RedirectView
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    path('', RedirectView.as_view(url='/game/', permanent=False)),
    path('game/', include(('game.urls', 'game'))),
    path('admin/', admin.site.urls),
]
