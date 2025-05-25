from django.urls import path
from . import views

urlpatterns = [
    path("api/graph/initial", views.initial_graph),
    path("api/graph/expand", views.expand_node),
]

