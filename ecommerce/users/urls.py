from django.urls import path
from . import views
urlpatterns = [
    path('login/',views.LoginView.as_view(),name="user login"),
    path('signup/',views.RegisterView.as_view(),name="user register"),
    path('logout/',views.LogoutView.as_view(),name="user logout"),
    path('<int:user_id>/', views.RegisterView.as_view(), name='user-detail'),
    path('dashboard/',views.DashboardView.as_view(),name='any protected route'),
]
