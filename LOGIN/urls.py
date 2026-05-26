from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from django.urls import path
from . import views
urlpatterns=[
    path('login/',views.mytoken.as_view()),
    path('login/refresh/',TokenRefreshView.as_view()),
    path('create/',views.CreateUser.as_view()),
    path('verify/<str:uuid>/<str:token>/',views.Verification.as_view()),
    path('employee-create/',views.EmployeeTemperary.as_view()),
    path('password-change/<str:pk>/',views.changePassword.as_view()),
    path('password-force-change/<str:pk>/',views.force_password_reset.as_view()),
    path('password-change-Founder/<str:pk>/',views.changePasswordByFounder.as_view())
]