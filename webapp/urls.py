from django.urls import path, re_path
from django.http import HttpResponse

from myapp import views as myapp_view

urlpatterns = [
    path('healthz', myapp_view.healthz, name='healthz'),
    path('ping', myapp_view.ping, name='ping'),

    # Add a catch-all path for undefined APIs
    re_path(r'^.*$', lambda request: HttpResponse(status=404)),
]
