from django.urls import path
from . import views

urlpatterns = [
    path('',views.home),
    path('minishop/',views.minishop),
    path('register/',views.register),
    path('login1/', views.login1),
    path('logout1/', views.logout1),
    path('create/', views.create),
    path('read/', views.read),
    path('singlepro/<int:id>/',views.singlepro),
    path('addcart/<int:id>/',views.addcart),
    path('deletecart/<int:id>/',views.deletecart),
    path('changequantity/<int:id>/',views.changequantity),
    path('cart/',views.cart),
    path('billing/',views.billing),


]
