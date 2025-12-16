from django.urls import path
from . import views

app_name = 'hotels'

urlpatterns = [
    path('', views.hotel_list, name='hotel_list'),
    path('hotel/<int:hotel_id>/', views.room_list, name='room_list'),
    path('room/<int:room_id>/', views.room_detail, name='room_detail'),
]


