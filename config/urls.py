from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from apps.accounts.views import HomeView
from config.views import icone, manifest

urlpatterns = [
    path('admin/', admin.site.urls),
    path('manifest.webmanifest', manifest, name='manifest'),
    path('marque/icone-<int:taille>.png', icone, name='icone'),
    path('favicon.ico', RedirectView.as_view(pattern_name='icone', permanent=False), {'taille': 32}),
    path('', HomeView.as_view(), name='home'),
    path('comptes/', include('apps.accounts.urls')),
    path('calendrier/', include('apps.scheduling.urls')),
    path('reservations/', include('apps.bookings.urls')),
    path('offres/', include('apps.offers.urls')),
    path('solde/', include('apps.purchases.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('actualites/', include('apps.actualites.urls')),
]
