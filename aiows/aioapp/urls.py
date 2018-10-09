# -*- coding: utf-8 -*-
from aiows.aioapp import views


patterns = [
    ('get', ['channel/{channel}/', views.channel_subscribe]),
    ('post', ['channel/{channel}/', views.channel_publish]),
    ('post', ['broadcast/', views.channel_publish_bulk]),
]
