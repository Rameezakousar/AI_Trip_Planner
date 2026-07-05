from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('plan-trip/', views.plan_trip, name='plan_trip'),

    # NEW
    path('trip/<int:trip_id>/', views.trip_detail, name='trip_detail'),
    path('trip/<int:trip_id>/delete/', views.delete_trip, name='delete_trip'),
    path('trip/<int:trip_id>/pdf/', views.download_pdf, name='download_pdf'),
    path("trip/<int:trip_id>/edit/", views.edit_trip, name="edit_trip"),
    path("profile/", views.profile, name="profile"),
    path(
    "trip/<int:trip_id>/favorite/",
    views.toggle_favorite,
    name="toggle_favorite"
),
    path("logout/", views.logout_view, name="logout"), 
]