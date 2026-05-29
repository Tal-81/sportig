from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    path('', views.TicketListView.as_view(), name='list'),
    path('create/', views.CreateTicketView.as_view(), name='create'),
    path('<int:ticket_id>/', views.TicketDetailView.as_view(), name='detail'),
]
