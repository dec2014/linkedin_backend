from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.tokens import AccessToken
from LOGIN.models import NewUser
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser


class Custom_middleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string=scope['query_string'].decode()
        token=query_string.split('token=')[-1]
        try:
            decoded_token=AccessToken(token)
            user_id=decoded_token['user_id']
            user=await self.get_user(user_id)
            scope['user']=user

        except:
            scope['user']=AnonymousUser()

            
        return await super().__call__(scope, receive, send)
    



    @database_sync_to_async
    def get_user(self,user_id,):
        try:
            return NewUser.objects.get(pk=user_id)
        except:
            return AnonymousUser()
        