from django.shortcuts import render
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import permissions,generics,mixins
from LOGIN.permission import is_Founder
from .serialization import OrganizatoinSerializers,BlogCreateSerialization,commentsCreateSerialization,BlogReadSerialization
from LOGIN.permission import is_Founder,Founder_Set_Up,BlogCreater,SameOrganizatoin,followPermissions,unfollowPermissions,BlogReadPermission,BlogUpdatePermissions,CommentsUpdatePermission,BlogDeletePermissions,employeeDeletePermission,delete_pin_permissions
from .consumers import organization
from .models import Organiztion,Blog,BlogNotification,FollowUnNotification,Tag,OrganizationFollower,OrganizationFollowing,BlogLike,BlogRead,Comments,Streak,PinBlog
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from LOGIN.models import NewUser,UserFollowing
from django.shortcuts import get_object_or_404
from django.db.models import Q,F,Count
from django.utils import timezone
# Create your views here.




class CreateOrganization(generics.CreateAPIView):
    serializer_class=OrganizatoinSerializers
    authentication_classes=[JWTAuthentication]
    permission_classes=[permissions.IsAuthenticated,is_Founder]
    def perform_create(self, serializer):
        user =self.request.user
        organization=serializer.save(founder=user)
        user.created_organization=True
        user.organization=organization
        user.save()



class CreateBlog(generics.CreateAPIView):
    queryset=Organiztion.objects.all()
    serializer_class=BlogCreateSerialization
    authentication_classes=[JWTAuthentication]
    lookup_field='Name'
    permission_classes=[permissions.IsAuthenticated,BlogCreater]
    def get_queryset(self):
        return Organiztion.objects.all()
    def create(self, request, *args, **kwargs):
        organization=self.get_object()
        if organization.id!=request.user.organization_id:
            return Response('not allowed')
        
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tag=serializer.validated_data.pop('tag')

        blog=serializer.save(created_by=request.user,organization_id=request.user.organization_id)
        for tags in tag:
            t,_=Tag.objects.get_or_create(name=tags)
            blog.tag.add(t)

        streak=Streak.objects.get(user_streak_id=request.user.id)
        time_now=timezone.now().date()
        if streak.last_activity_date is None:
            streak.last_activity_date=time_now
            streak.count=1
            if streak.max_streak<streak.count:
                streak.max_streak=streak.count
            streak.save()
        else:
            last_acitivity=streak.last_activity_date.date()
            differnce=time_now-last_acitivity
            if differnce.days==0:
                pass
            elif differnce.days==1:
                streak.last_activity_date=time_now
                streak.count+=1
                if streak.max_streak<streak.count:
                    streak.max_streak=streak.count
                streak.save()
            else:
                streak.last_activity_date=time_now
                streak.count=0
                streak.save()
        
        channel_layer=get_channel_layer()
        room=f'notification_{organization.Name}'
        async_to_sync(channel_layer.group_send)(room,{
            'type':'blog_notification',
            'id':blog.id,
            'content':blog.content,
            'created_by':blog.created_by.user_name,
            'created_at':str(blog.created_at),
            'user_name':self.request.user.user_name
        })
        return Response(serializer.data)
    
        



class follow(generics.UpdateAPIView):
    queryset=Organiztion.objects.all()
    serializer_class=OrganizatoinSerializers
    lookup_field='Name'
    authentication_classes=[JWTAuthentication]
    permission_classes=[permissions.IsAuthenticated,followPermissions]
    def update(self, request, *args, **kwargs):
        obj=self.get_object()
        channel_layer=get_channel_layer()
        current_user=NewUser.objects.select_related('organization').get(pk=request.user.id)
        if current_user.role==NewUser.roles.EMPLOYEE:
            UserFollowing.objects.create(user_id=current_user.id,following_id=obj.id)
            room=f'user_{current_user.id}'
            async_to_sync(channel_layer.group_send)(room,{
                'type':'follower_employee',
                'name':obj.Name,

            })
            room2=f'user_{obj.founder_id}'
            content=f'{current_user.user_name} started following your organization'
            FollowUnNotification.objects.create(content=content,owner_id=obj.founder_id,user_id=current_user.id)
            async_to_sync(channel_layer.group_send)(room2,{
                'type':'follower_employee_to_founder',
                'content':content,


            })
        else:
            UserFollowing.objects.create(user_id=current_user.id,following_id=obj.id)
            current_organization=current_user.organization
            OrganizationFollowing.objects.create(organization_id=current_organization.id,following_id=obj.id)
            OrganizationFollower.objects.create(organization_id=obj.id,follower_id=current_organization.id)


            room=f'organization_{current_organization.Name}'
            async_to_sync(channel_layer.group_send)(room,{
                'type':'follower_founder',
                'name':obj.Name,

            })
            room2=f'user_{obj.founder_id}'
            content=f'{current_user.user_name} founder of {current_organization.Name} started following your organization'
            FollowUnNotification.objects.create(content=content,owner_id=obj.founder_id,user_id=current_user.id)
            async_to_sync(channel_layer.group_send)(room2,{
                'type':'follower_employee_to_founder',
                'content':content,


            })
        return Response('followed successfully')
        
        


        


class unfollow(generics.UpdateAPIView):
    queryset=Organiztion.objects.all()
    serializer_class=OrganizatoinSerializers
    lookup_field='Name'
    authentication_classes=[JWTAuthentication]
    permission_classes=[permissions.IsAuthenticated,unfollowPermissions]
    def update(self, request, *args, **kwargs):
        obj=self.get_object()
        channel_layer=get_channel_layer()
        current_user=NewUser.objects.select_related('organization').get(pk=request.user.id)
        if current_user.role==NewUser.roles.EMPLOYEE:
            UserFollowing.objects.get(user_id=current_user.id, following_id=obj.id).delete()
            
            room=f'user_{current_user.id}'
            async_to_sync(channel_layer.group_send)(room,{
                'type':'unfollower_employee',
                'name':obj.Name,

            })
            room2=f'user_{obj.founder_id}'
            content=f'{current_user.user_name} started following your organization'
            FollowUnNotification.objects.create(content=content,owner_id=obj.founder_id,user_id=current_user.id)
            async_to_sync(channel_layer.group_send)(room2,{
                'type':'unfollower_employee_to_founder',
                'content':content,


            })
        else:
            UserFollowing.objects.get(user_id=current_user.id, following_id=obj.id).delete()
            
            
            current_organization=current_user.organization
            OrganizationFollowing.objects.get(organization_id=current_organization.id,following_id=obj.id).delete()
            OrganizationFollower.objects.get(follower_id=current_organization.id,organization_id=obj.id).delete()

            room=f'organization_{current_organization.Name}'
            async_to_sync(channel_layer.group_send)(room,{
                'type':'unfollower_founder',
                'name':obj.Name,

            })
            room2=f'user_{obj.founder_id}'
            content=f'{current_user.user_name} founder of {current_organization.Name} unfollowed your organization'
            FollowUnNotification.objects.create(content=content,owner_id=obj.founder_id,user_id=current_user.id)
            async_to_sync(channel_layer.group_send)(room2,{
                'type':'unfollower_employee_to_founder',
                'content':content,


            })
        return Response('unfollowed successfully')
    

class Blog_read(generics.CreateAPIView):
    queryset=Blog.objects.all()
    serializer_class=BlogCreateSerialization
    lookup_field='pk'
    authentication_classes=[JWTAuthentication]
    permission_classes=[permissions.IsAuthenticated,BlogCreater]
    
    def create(self, request, *args, **kwargs):
        blog=Blog.objects.select_related('organization').get(id=kwargs.get('pk'))
        serializer=BlogCreateSerialization(blog)
        user_following=UserFollowing.objects.filter(user_id=request.user.id,following_id=blog.organization_id).exists()
        organization_following=OrganizationFollowing.objects.filter(organization_id=request.user.organization_id,following_id=blog.organization_id).exists()
        if blog.organization_id==request.user.organization_id or user_following or organization_following or blog.organization.type==Organiztion.types.PUBLIC:
            BlogRead.objects.get_or_create(blog=blog,read_by_id=request.user.id)

            streak=Streak.objects.get(user_streak_id=request.user.id)
            time_now=timezone.now().date()
            if streak.last_activity_date is None:
                streak.last_activity_date=time_now
                streak.count=1
                if streak.max_streak<streak.count:
                    streak.max_streak=streak.count
                streak.save()
            else:
                last_acitivity=streak.last_activity_date.date()
                differnce=time_now-last_acitivity
                if differnce.days==0:
                    pass
                elif differnce.days==1:
                    streak.last_activity_date=time_now
                    streak.count+=1
                    if streak.max_streak<streak.count:
                        streak.max_streak=streak.count
                    streak.save()
                else:
                    streak.last_activity_date=time_now
                    streak.count=0
                    streak.save()
            return Response(serializer.data)
        return Response('you cannot read this post/blog')
    

class blogLike(generics.GenericAPIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[permissions.IsAuthenticated,BlogCreater]
    def post(self,request,*args,**kwargs):
        blog=Blog.objects.select_related('organization').get(id=kwargs.get('pk'))
        userfollowing=UserFollowing.objects.select_related('following').filter(user_id=request.user.id,following_id=blog.organization_id).exists()
        organizationfollowing=OrganizationFollowing.objects.filter(organization_id=request.user.organization_id,following_id=blog.organization_id).exists()
        if blog.organization_id==request.user.organization_id or userfollowing or organizationfollowing or blog.organization.type == Organiztion.types.PUBLIC:
            obj,created=BlogLike.objects.update_or_create(
                blog=blog,
                like_user_id=request.user.id,
            )
            if not created:
                obj.like= not obj.like
                obj.save()


            streak=Streak.objects.get(user_streak_id=request.user.id)
            time_now=timezone.now().date()
            if streak.last_activity_date is None:
                streak.last_activity_date=time_now
                streak.count=1
                if streak.max_streak<streak.count:
                    streak.max_streak=streak.count
                streak.save()
            else:
                last_acitivity=streak.last_activity_date.date()
                differnce=time_now-last_acitivity
                if differnce.days==0:
                    pass
                elif differnce.days==1:
                    streak.last_activity_date=time_now
                    streak.count+=1
                    if streak.max_streak<streak.count:
                        streak.max_streak=streak.count
                    streak.save()
                else:
                    streak.last_activity_date=time_now
                    streak.count=0
                    streak.save()

            return Response({'like':obj.like,'created':created})
        return Response('error not given permission')




class BlogUpdate(generics.UpdateAPIView):
    queryset=Blog.objects.all()
    serializer_class=BlogCreateSerialization
    lookup_field='pk'
    authentication_classes=[JWTAuthentication]
    permission_classes=[permissions.IsAuthenticated,BlogCreater,BlogUpdatePermissions]
    def perform_update(self, serializer):
        blog=serializer.instance

        tag2=serializer.validated_data.pop('tag')
        a=[]
        for tags in tag2:
            t,_=Tag.objects.get_or_create(name=tags)
            a.append(t)
        if a is not None:
            blog.tag.set(a)
        

        return super().perform_update(serializer)
    


class BlogDelete(generics.DestroyAPIView):
    queryset=Blog.objects.all()
    serializer_class=BlogCreateSerialization
    lookup_field='pk'
    authentication_classes=[JWTAuthentication]
    permission_classes=[permissions.IsAuthenticated,BlogCreater,BlogDeletePermissions]
    def get_queryset(self):
        return Blog.objects.select_related('organization').all()
        


class CreateComments(generics.CreateAPIView):
    serializer_class=commentsCreateSerialization
    authentication_classes=[JWTAuthentication]
    permission_classes=[permissions.IsAuthenticated,BlogCreater]
    def create(self, request, *args, **kwargs):
        self.obj=Blog.objects.select_related('organization').get(id=kwargs.get('pk'))
        if self.obj.organization.type=='Pvt':
            following=UserFollowing.objects.select_related('following').filter(user_id=request.user.id).values_list('following__Name',flat=True)
            organizationfollowing=OrganizationFollowing.objects.select_related('following').filter(organization_id=request.user.organization_id).values_list('following__Name',flat=True)
            if request.user.organization==self.obj.organization:
                return super().create(request, *args, **kwargs)
            elif self.obj.organization.Name in following:
                return super().create(request, *args, **kwargs)
            elif self.obj.organization.Name in organizationfollowing :
                return super().create(request, *args, **kwargs)
            else:
                return Response('no permissions')
        elif self.obj.organization.type=='Pub':
            return super().create(request, *args, **kwargs)
        else:
            return Response('no permissions')

    def perform_create(self, serializer):
        serializer.save(owner_id=self.request.user.id,blog_id=self.obj.id)
        streak=Streak.objects.get(user_streak_id=self.request.user.id)
        time_now=timezone.now().date()
        if streak.last_activity_date is None:
            streak.last_activity_date=time_now
            streak.count=1
            if streak.max_streak<streak.count:
                streak.max_streak=streak.count
            streak.save()
        else:
            last_acitivity=streak.last_activity_date.date()
            differnce=time_now-last_acitivity
            if differnce.days==0:
                pass
            elif differnce.days==1:
                streak.last_activity_date=time_now
                streak.count+=1
                if streak.max_streak<streak.count:
                    streak.max_streak=streak.count
                streak.save()
            else:
                streak.last_activity_date=time_now
                streak.count=0
                streak.save()
        channel_layer=get_channel_layer()
        room=f'notification_{self.obj.organization.Name}'
        async_to_sync(channel_layer.group_send)(room,{
            'type':'comments',
            'id':serializer.data['owner'],
            'content':serializer.data['text'],
            
        })


        
class CommentsUpdate(generics.UpdateAPIView):
    queryset=Comments.objects.all()
    serializer_class=commentsCreateSerialization
    lookup_field='pk'
    authentication_classes=[JWTAuthentication]
    permission_classes=[permissions.IsAuthenticated,BlogCreater,CommentsUpdatePermission]
    def get_queryset(self):
        return Comments.objects.select_related('blog__organization').all()
    def perform_update(self, serializer):

        serializer.save()
        
        channel_layer=get_channel_layer()
        room=f'notification_{serializer.instance.blog.organization.Name}'
        async_to_sync(channel_layer.group_send)(room,{
            'type':'comments_update',
            'id':serializer.data['owner'],
            'content':serializer.data['text'],
            
        })
    

class CommentsDelete(generics.DestroyAPIView):
    queryset=Comments.objects.all()
    lookup_field='pk'
    authentication_classes=[JWTAuthentication]
    permission_classes=[permissions.IsAuthenticated,BlogCreater,CommentsUpdatePermission]
    def get_queryset(self):
        return Comments.objects.select_related('blog__organization').all()
    def perform_destroy(self, instance):
        id=instance.id
        instance.delete()
        channel_layer=get_channel_layer()
        room=f'notification_{instance.blog.organization.Name}'
        async_to_sync(channel_layer.group_send)(room,{
            'type':'comments_delete',
            'id':id,

            
        })




class SearchingBlogs(generics.ListAPIView):
    queryset=Blog.objects.all()
    serializer_class=BlogReadSerialization
    authentication_classes=[JWTAuthentication]
    permission_classes=[permissions.IsAuthenticated,BlogCreater]
    def get_queryset(self):
        following=UserFollowing.objects.select_related('following').filter(user_id=self.request.user.id).values_list('following__Name',flat=True)
        organizationfollowing=OrganizationFollowing.objects.select_related('following').filter(organization_id=self.request.user.organization_id).values_list('following__Name',flat=True)
        search=self.request.query_params.get('search',None)
        return Blog.objects.select_related('organization').prefetch_related('tag').filter(Q(title__icontains=search)|
                                                                  Q(organization__Name__icontains=search)|
                                                                  Q(tag__name__icontains=search)).filter(
                                                                      Q(organization_id=self.request.user.organization_id)|
                                                                      Q(organization__Name__in=organizationfollowing)|
                                                                      Q(organization_id__in=following)
                                                                      ).distinct()
    




class EmployeeAnalytics(generics.RetrieveAPIView):
    queryset=Blog.objects.all()
    serializer_class=BlogReadSerialization
    authentication_classes=[JWTAuthentication]
    permission_classes=[permissions.IsAuthenticated,BlogCreater]
    def get(self, request, *args, **kwargs):
        total_post=Blog.objects.select_related('organization').filter(created_by_id=kwargs.get('pk')).count()
        total_comments=Comments.objects.filter(owner_id=kwargs.get('pk')).count()
        total_likes=BlogLike.objects.filter(like_user_id=kwargs.get('pk'),like=True).count()
        total_reads=BlogRead.objects.filter(read_by_id=kwargs.get('pk')).count()
        streak=Streak.objects.get(user_streak_id=kwargs.get('pk'))
        count=streak.count
        max_streak=streak.max_streak
        return Response({'total_post':total_post,'total_comments':total_comments,'total_likes':total_likes,'total_reads':total_reads,'count':count,'max_streak':max_streak})
    


class OrganizationAnalytics(generics.RetrieveAPIView):
    queryset=Organiztion.objects.all()
    serializer_class=OrganizatoinSerializers
    authentication_classes=[JWTAuthentication]
    permission_classes=[permissions.IsAuthenticated,BlogCreater]
    def get(self, request, *args, **kwargs):
        from LOGIN.models import NewUser
        total_employee=NewUser.objects.filter(organization_id=kwargs.get('pk')).count()
        total_blog=Blog.objects.filter(organization_id=kwargs.get('pk')).count()
        total_read=BlogRead.objects.select_related('blog').filter(blog__organization_id=kwargs.get('pk')).count()
        total_followers=OrganizationFollower.objects.filter(organization_id=kwargs.get('pk')).count()
        top_employee=Streak.objects.select_related('user_streak').filter(user_streak__organization_id=kwargs.get('pk')).order_by('-count').first().user_streak.user_name
        top_post_id=BlogLike.objects.filter(blog__organization_id=kwargs.get('pk'),like=True).values('blog').annotate(total=Count('blog')).order_by('-total').first()
        if top_post_id:
            top_post_id=top_post_id['blog']
            top_post=Blog.objects.get(id=top_post_id)
            serializer=BlogReadSerialization(top_post)
            return Response({'total_employee':total_employee,'total_blog':total_blog,'total_read':total_read,'total_followers':total_followers,'top_employee':top_employee,'top_post':serializer.data})
        return Response({'total_employee':total_employee,'total_blog':total_blog,'total_read':total_read,'total_followers':total_followers,'top_employee':top_employee,'top_post':'no likes'})



    

class Organization_update(generics.UpdateAPIView):
    queryset=Organiztion.objects.all()
    serializer_class=OrganizatoinSerializers
    lookup_field='pk'
    authentication_classes=[JWTAuthentication]
    permission_classes=[permissions.IsAuthenticated,BlogCreater,SameOrganizatoin]



class employeeDelete(generics.DestroyAPIView):
    queryset=NewUser.objects.all()
    lookup_field='pk'
    authentication_classes=[JWTAuthentication]
    permission_classes=[permissions.IsAuthenticated,BlogCreater,employeeDeletePermission]




class Pin_Blog(generics.CreateAPIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[permissions.IsAuthenticated,BlogCreater]
    def create(self, request, *args, **kwargs):
        blog=Blog.objects.get(id=kwargs.get('pk'))
        if request.user.organization_id==blog.organization_id and request.user.role=='F':
            PinBlog.create(blog=blog)
            return Response('pinned Blog')
        return Response('no permission')
    
    
class unPinBlog(generics.DestroyAPIView):
    queryset=PinBlog.objects.all()
    lookup_field='pk'
    authentication_classes=[JWTAuthentication]
    permission_classes=[permissions.IsAuthenticated,BlogCreater,delete_pin_permissions]
    def get_queryset(self):
        return PinBlog.objects.select_related('blog').all()
        