from django.urls import path
from todo import views

urlpatterns = [
    path('', views.index, name='index'),  # points to the index view
    # other paths...
]
