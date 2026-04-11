from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('game/<int:game_id>/', views.game_view, name='game'),
    path('attack/<int:game_id>/', views.attack, name='attack'),
    path('heavy/<int:game_id>/', views.heavy, name='heavy'),
    path('quick/<int:game_id>/', views.quick, name='quick'),
    path('defend/<int:game_id>/', views.defend, name='defend'),
    path('counter/<int:game_id>/', views.counter, name='counter'),
    path('dodge/<int:game_id>/', views.dodge, name='dodge'),
    path('special/<int:game_id>/', views.special, name='special'),
    path('restart/<int:game_id>/', views.restart, name='restart'),
]