"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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

from django.contrib import admin
from django.urls import path, include
from .views import home, auth_page, attendance_page

urlpatterns = [
    path('admin/', admin.site.urls),

    # Frontend Pages
    path('', home),                 # http://127.0.0.1:8000/
    path('auth/', auth_page),       # http://127.0.0.1:8000/auth/
    path('attendance/', attendance_page), #http://127.0.0.1:8000/attendance/

    # API Routes
    path('accounts/', include('accounts.urls')),
]

