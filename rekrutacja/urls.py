"""
URL configuration for rekrutacja project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, re_path
from calendar_events import views
from django.conf.urls import handler404

urlpatterns = [
    path("", views.start, name='start'),
    re_path(r'^(?P<year>-?\d+)/$', views.start_year, name='start_year'),
    re_path(r'^(?P<year>-?\d+)/(?P<month>-?\d+)/$', views.calendar_view, name='calendar_view'),
    re_path(r'^(?P<year>-?\d+)/(?P<month>-?\d+)/(?P<day>\d+)/$', views.day_view, name='day_view'),
]

handler404 = views.not_found_view