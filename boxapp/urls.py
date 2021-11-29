from django.urls import path
from . import views
from .views import BoxClass

urlpatterns = [
    path('register', views.registerUser),
    path('login', views.loginUser),
    path('myboxes',views.myBoxes),
    path('allboxes',views.allBoxes),
    path('box',views.addBox),
    path('box/<str:pk>',BoxClass.as_view()),
]