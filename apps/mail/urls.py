from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('bandeja/', views.inbox_view, name='inbox'),
    path('bandeja/vaciar/', views.inbox_clear_api, name='inbox_clear'),
    path('bandeja/<int:pk>/leido/', views.mark_email_read_api, name='mark_email_read'),
    path('enviados/', views.sent_view, name='sent_list'),
    path('enviados/mas/', views.sent_more_api, name='sent_more'),
    path('enviados/vaciar/', views.sent_empty_api, name='sent_empty'),
    path('papelera/', views.trash_view, name='trash_list'),
    path('papelera/mas/', views.trash_more_api, name='trash_more'),
    path('papelera/restaurar/', views.trash_restore_api, name='trash_restore'),
    path('papelera/eliminar/', views.trash_delete_api, name='trash_delete'),
    path('papelera/vaciar/', views.trash_empty_api, name='trash_empty'),
    path('borradores/', views.drafts_view, name='drafts_list'),
    path('borradores/mas/', views.drafts_more_api, name='drafts_more'),
    path('borradores/<int:pk>/', views.draft_get_api, name='draft_get'),
]
