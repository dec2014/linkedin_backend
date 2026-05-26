from django.urls import path
from . import views

urlpatterns=[
    path('create-organizaiton/',views.CreateOrganization.as_view()),
    path('create-blog/<str:Name>/',views.CreateBlog.as_view()),
    path('follow/<str:Name>/',views.follow.as_view()),
    path('unfollow/<str:Name>/',views.unfollow.as_view()),
    path('blog-read/<str:pk>/',views.Blog_read.as_view()),
    path('blog-like/<str:pk>/',views.blogLike.as_view()),
    path('blog-update/<str:pk>/',views.BlogUpdate.as_view()),
    path('blog-delete/<str:pk>/',views.BlogDelete.as_view()),
    path('comment-create/<str:pk>/',views.CreateComments.as_view()),
    path('comment-update/<str:pk>/',views.CommentsUpdate.as_view()),
    path('comment-delete/<str:pk>/',views.CommentsDelete.as_view()),
    path('searching-for/',views.SearchingBlogs.as_view()),
    path('employee-analytics/<str:pk>/',views.EmployeeAnalytics.as_view()),
    path('organization-analytics/<str:pk>/',views.OrganizationAnalytics.as_view()),
    path('organization-update/<str:pk>/',views.Organization_update.as_view()),
    path('employee-delete/<str:pk>/',views.employeeDelete.as_view()),
    path('pin-blog/<str:pk>/',views.Pin_Blog.as_view()),
    path('unpin-blog/<str:pk>/',views.unPinBlog.as_view()),
]