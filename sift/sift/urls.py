# -*- coding: utf-8 -*-
# sift/urls.py

"""sift URL Configuration"""

from django.conf.urls import url, include
#from django.contrib import admin

from concerts.views import Home

urlpatterns = [
    url(r'^concerts/', include('concerts.urls')),
    url(r'^$', Home.as_view(), name='sift_home'),
    #url(r'^admin/', admin.site.urls),
]
