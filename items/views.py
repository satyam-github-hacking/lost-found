from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from items import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),

    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('lost/add/', views.add_lost_item, name='add_lost_item'),
    path('found/add/', views.add_found_item, name='add_found_item'),

    path('item/<int:pk>/', views.item_detail, name='item_detail'),

    path('item/<int:pk>/edit/', views.edit_item, name='edit_item'),
    path('item/<int:pk>/delete/', views.delete_item, name='delete_item'),

    path('item/<int:pk>/resolve/', views.mark_resolved, name='mark_resolved'),
    path('item/<int:pk>/reopen/', views.reopen_item, name='reopen_item'),

    path('item/<int:pk>/message/', views.send_message, name='send_message'),

    path('inbox/', views.inbox, name='inbox'),

    path(
        'conversation/<int:item_pk>/<int:other_user_pk>/',
        views.conversation,
        name='conversation'
    ),
]

# MEDIA FILES
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
