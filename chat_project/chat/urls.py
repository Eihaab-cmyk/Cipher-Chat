from django.urls import path
from django.shortcuts import render
from . import views

urlpatterns = [
    path("", views.home, name='home'),
    path("api/register-public-key/", views.register_public_key, name='register_public_key'),
    path("api/get-public-key/<int:user_id>/", views.get_public_key, name='get_public_key'),
    path("api/get-users-public-keys/", views.get_users_public_keys, name='get_users_public_keys'),
    path("api/search-users/", views.search_users, name='search_users'),
    path("api/start-chat/<int:user_id>/", views.start_private_chat, name='start_chat'),
    path("api/my-chats/", views.my_chats, name='my_chats'),
    path("api/messages/<int:chat_id>/", views.get_messages, name='get_messages'),
    path("api/create-group/", views.create_group, name='create_group'),
    path('api/get-my-encrypted-key/', views.get_my_encrypted_key, name='get_my_encrypted_key'),
]