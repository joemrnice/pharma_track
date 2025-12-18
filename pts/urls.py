from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('drugs/', views.drug_list, name='drug_list'),
    path('drugs/create/', views.drug_create, name='drug_create'),
    path('drugs/<int:pk>/update/', views.drug_update, name='drug_update'),
    path('drugs/<int:pk>/delete/', views.drug_delete, name='drug_delete'),
    path('transactions/create/', views.transaction_create, name='transaction_create'),
    path('stocks/', views.stock_list, name='stock_list'),  # Added for viewing stocks
]