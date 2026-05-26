from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework.response import Response
import json
from .models import Organiztion,Blog,BlogNotification,OrganizationFollower,OrganizationFollowing
from LOGIN.models import NewUser,UserFollowing
from asgiref.sync import sync_to_async


class organization(AsyncWebsocketConsumer):
    async def connect(self):
        print('connected')
        self.user=self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return Response('user not logged in.')
        
        self.group_user=f'user_{self.user.id}'
        organization=await self.get_organization()
        self.group_organization=f'organization_{organization.Name}'
        self.notification_organization_group=f'notification_{organization.Name}'
        self.user_followings=await self.user_following()
        self.organization_followings= await self.organization_following()

        self.followings=set(self.user_followings + self.organization_followings)
        await self.channel_layer.group_add(self.group_organization,self.channel_name)
        await self.channel_layer.group_add(self.notification_organization_group,self.channel_name)
        await self.channel_layer.group_add(self.group_user,self.channel_name)
        if self.followings:
            for following in self.followings:
                notification=f'notification_{following}'
                await self.channel_layer.group_add(notification,self.channel_name)
        await self.accept()
            

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_organiztion,self.channel_name)
        await self.channel_layer.group_discard(self.notification_organization_group,self.channel_name)
        await self.channel_layer.group_discard(self.group_user,self.channel_name)

    
    async def receive(self, text_data = None, bytes_data = None):
        return await super().receive(text_data, bytes_data)
    

    async def blog_notification(self,event):
        if event['user_name']!=self.user.user_name:
            await self.BlogCreation(event)
            await self.send(text_data=json.dumps(event))



    async def follower_employee(self,event):
        room=f'notification_{event["name"]}'
        await self.channel_layer.group_add(room,self.channel_name)


    async def follower_employee_to_founder(self,event):
        await self.send(text_data=json.dumps(event))


    async def follower_founder(self,event):
        room=f'notification_{event["name"]}'
        await self.channel_layer.group_add(room,self.channel_name)



    async def unfollower_employee(self,event):
        room=f'notification_{event["name"]}'
        await self.channel_layer.group_discard(room,self.channel_name)


    async def comments(self,event):
        await self.send(text_data=json.dumps(event))


    async def comments_update(self,event):
        await self.send(text_data=json.dumps(event))


    async def comments_delete(self,event):
        await self.send(text_data=json.dumps(event))



    async def unfollower_founder(self,event):
        room=f'notification_{event["name"]}'
        await self.channel_layer.group_discard(room,self.channel_name)


    async def unfollower_employee_to_founder(self,event):
        await self.send(text_data=json.dumps(event))


    @sync_to_async
    def organization_following(self):
        organization=list(OrganizationFollowing.objects.select_related('following').filter(organization_id=self.user.organization_id).values_list('following__Name',flat=True))
        return organization    

    @sync_to_async
    def get_organization(self):
        return Organiztion.objects.get(id=self.user.organization_id)


    @sync_to_async
    def user_following(self):
        user=list(UserFollowing.objects.select_related('following').filter(user_id=self.user.id).values_list('following__Name',flat=True))
        return user
    


    @sync_to_async
    def BlogCreation(self,event):
        BlogNotification.objects.create(blog_id=event['id'],sent_to_id=self.user.id)

        return True



        
