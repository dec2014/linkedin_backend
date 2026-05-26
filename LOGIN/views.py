from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from .models import NewUser
from .serialization import UserCreateSerializer,UserCreateEmployeeSerializer,changePasswordSerializer,MyTokenObtainPairSerializer
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .email import EmailVerification,TempEmployeeCredentials
from rest_framework import permissions
from BLOG.models import Streak
from rest_framework_simplejwt.authentication import JWTAuthentication
from .permission import is_temp_pass,is_Founder,Founder_Set_Up,BlogCreater
from BLOG.models import Organiztion
from rest_framework_simplejwt.views import TokenObtainPairView

# Create your views here.
class CreateUser(generics.CreateAPIView):
    queryset=NewUser.objects.all()
    serializer_class=UserCreateSerializer
    def perform_create(self, serializer):
        serializer.save()
        Streak.objects.create(user_streak_id=serializer.data['id'])
        
    

class Verification(generics.RetrieveAPIView):
    serializer_class=UserCreateSerializer
    def retrieve(self, request, *args, **kwargs):
        u=kwargs.get('uuid')
        uuid=urlsafe_base64_decode(u).decode()
        try:
            user=NewUser.objects.get(pk=uuid)
        except:
            return Response('not valid')
        token=kwargs.get('token','')
        if default_token_generator.check_token(user,token):
            user.is_verified=True
            user.save()
            return Response('verification successfull')
        return Response('verification failed')
        


class EmployeeTemperary(generics.CreateAPIView):
    queryset=NewUser.objects.all()
    serializer_class=UserCreateEmployeeSerializer
    authentication_classes=[JWTAuthentication]
    permission_classes=[permissions.IsAuthenticated,Founder_Set_Up]
    def create(self, request, *args, **kwargs):


        email=request.data.get('email','')
        password=request.data.get('password','')
        TempEmployeeCredentials(email,password)
        serializer=self.get_serializer(data=request.data)
        if serializer.is_valid():
            
            organization=Organiztion.objects.get(founder=request.user)
            # user.organization=organization
            serializer.save(is_password_temp=True,organization=organization)
            Streak.objects.create(user_streak_id=serializer.data['id'])
            return Response(serializer.data)
        return Response(serializer.errors)
    


class changePassword(generics.UpdateAPIView):
    queryset=NewUser.objects.all()
    serializer_class=changePasswordSerializer
    authentication_classes=[JWTAuthentication]
    permission_classes=[permissions.IsAuthenticated,is_temp_pass]
    def update(self, request, *args, **kwargs):
        if request.user.id==kwargs.get('pk'):
            user=request.user
            serializer=self.get_serializer(user,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response('password changed')
        return Response('error:password not changed')
    

class force_password_reset(generics.UpdateAPIView):
    queryset=NewUser.objects.all()
    authentication_classes=[JWTAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    def update(self, request, *args, **kwargs):
        user=NewUser.objects.get(id=kwargs.get('pk'))
        if request.user.organization_id==user.organization_id and request.user.role=='F' and request.user.id!=user.id:
            user.is_password_temp=True
            user.save()
            return Response('done')
        return Response('no permission')



class changePasswordByFounder(generics.UpdateAPIView):
    queryset=NewUser.objects.all()
    serializer_class=changePasswordSerializer
    authentication_classes=[JWTAuthentication]
    permission_classes=[permissions.IsAuthenticated,Founder_Set_Up]
    def update(self, request, *args, **kwargs):
        user=NewUser.objects.get(id=kwargs.get('pk'))
        if request.user.organization_id==user.organization_id and request.user.role=='F' and request.user.id!=user.id:
            password=request.data.get('password','')
            email=user.email
            serializer=self.get_serializer(user,data=request.data)
            if serializer.is_valid():
                serializer.save()
                TempEmployeeCredentials(email,password)
                return Response('password changed')
        return Response('error:password not changed')
        


class mytoken(TokenObtainPairView):
    serializer_class=MyTokenObtainPairSerializer
        
        
        