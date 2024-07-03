from django.urls import path, include
# Импортируем созданное нами представление
from .views import (PostsList, PostDetail,
                    PostFilterView, create_post,
                    edit_post, delete_post, AppointementView)


urlpatterns = [
        path('', PostsList.as_view(),name='main_page'),
        path('<int:pk>/',PostDetail.as_view()),
        path('search/', PostFilterView.as_view()),
        path('create/', create_post,name='Create post'),
        path('<int:pk>/edit/',edit_post, name='Update post'),
        path('<int:pk>/delete/', delete_post, name='Delete'),
        path('mail/', AppointementView.as_view(), name='news:mail')
                      ]