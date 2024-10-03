from django.urls import path
from . import views
urlpatterns = [
    path('login/',views.LoginView.as_view(),name="user login"),
    path('signup/',views.RegisterView.as_view(),name="user register"),
    # path('logout/',views.logout),
    path('dashboard/',views.DashboardView.as_view(),name='any protected route'),
]
