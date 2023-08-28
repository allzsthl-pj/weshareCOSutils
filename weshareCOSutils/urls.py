"""
URL configuration for weshareCOSutils project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from credentialUtils import views

urlpatterns = [
    path('print/bucket/', views.print_out_bucket_names),
    path('images/list/', views.get_images_list),
    path('images/url/', views.get_images_url),
    path('files/list/', views.get_files_list),
    path('files/url/', views.get_files_url),
    path('del/image/', views.delete_image),
    path('del/file/', views.delete_file),
    path('upload/image/', views.upload_image),
    path('upload/file/', views.upload_file),

]
