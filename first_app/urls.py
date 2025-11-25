from django.urls import path
from . import views

urlpatterns = [
    # Основные страницы
    path('', views.home, name='home'),
    path('promotions/', views.promotions, name='promotions'),
    path('dish/<slug:slug>/', views.dish_detail, name='dish_detail'),

    # Корзина
    path('cart/', views.корзина, name='корзина'),
    path('cart/add/<int:dish_id>/', views.добавить_в_корзину, name='добавить_в_корзину'),

    # Заказы
    path('checkout/', views.оформление_заказа, name='оформление_заказа'),
    path('orders/', views.история_заказов, name='история_заказов'),
    path('orders/<int:order_id>/', views.детали_заказа, name='детали_заказа'),

    # Отзывы и избранное
    path('review/<int:dish_id>/', views.добавить_отзыв, name='добавить_отзыв'),
    path('favorites/', views.избранное, name='избранное'),
    path('favorites/toggle/<int:dish_id>/', views.добавить_в_избранное, name='добавить_в_избранное'),

    # Профиль
    path('profile/', views.профиль, name='профиль'),

    # AJAX поиск
    path('search/', views.поиск, name='поиск'),

    # Регистрация
    path('register/', views.register, name='register'),
]