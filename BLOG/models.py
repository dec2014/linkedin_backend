from django.db import models
from django.db.models import Q,F

from django.utils import timezone
from datetime import datetime,time
# from LOGIN.models import NewUser
fixed_date=datetime.combine(timezone.now().date(),time(0,0))
# Create your models here.
class Organiztion(models.Model):
    class types(models.TextChoices):
        PRIVATE='Pvt','Private'
        PUBLIC= 'Pub','Public'
    Name=models.CharField(max_length=255,unique=True)
    founder=models.OneToOneField('LOGIN.NewUser',on_delete=models.CASCADE)
    bio_pitcure=models.ImageField(upload_to='organizationProfile/',null=True,blank=True)
    type=models.CharField(choices=types.choices,default=types.PRIVATE,max_length=3)
    body=models.TextField()


class OrganizationFollower(models.Model):
    organization=models.ForeignKey(Organiztion,on_delete=models.CASCADE,related_name='organization_follower')
    follower=models.ForeignKey(Organiztion,on_delete=models.CASCADE,null=True)
    class Meta:
        unique_together=['organization','follower'],

        constraints=[
            models.CheckConstraint(
                check=~Q(organization=F('follower')),
                name='organization_cannot_become_follower_of_itself'
            )
        ]



class OrganizationFollowing(models.Model):
    organization=models.ForeignKey(Organiztion,on_delete=models.CASCADE,related_name='organization_following')
    following=models.ForeignKey(Organiztion,on_delete=models.CASCADE,null=True)
    class Meta:
        unique_together=['organization','following']
        constraints=[
            models.CheckConstraint(
                check=~Q(organization=F('following')),
                name='organization_cannot_follow_itself'
            )
        ]



class Tag(models.Model):
    name=models.CharField(max_length=255)

class Blog(models.Model):
    title=models.CharField(max_length=255)
    content=models.TextField()
    pictures=models.ImageField(upload_to='blog_profiles',null=True,blank=True)
    created_by=models.ForeignKey('LOGIN.NewUser',on_delete=models.PROTECT)
    created_at=models.DateTimeField(auto_now=True)
    organization=models.ForeignKey(Organiztion,on_delete=models.CASCADE)
    tag=models.ManyToManyField(Tag)


class PinBlog(models.Model):
    blog=models.OneToOneField('Blog',on_delete=models.CASCADE,related_name='pinnedblog')


class BlogLike(models.Model):
    blog=models.ForeignKey(Blog,on_delete=models.CASCADE,related_name='blog_like')
    like=models.BooleanField(default=True)
    like_user=models.ForeignKey('LOGIN.NewUser',on_delete=models.CASCADE)
    class Meta:
        unique_together=['blog','like_user']



class BlogRead(models.Model):
    blog=models.ForeignKey(Blog,on_delete=models.CASCADE,null=True,blank=True,related_name='blog_read')
    read_by=models.ForeignKey('LOGIN.NewUser',on_delete=models.CASCADE,null=True,blank=True)
    class Meta:
        unique_together=['blog','read_by']

class BlogNotification(models.Model):
    blog=models.ForeignKey(Blog,on_delete=models.CASCADE,related_name='blog_notification')
    read=models.BooleanField(default=False,db_index=True)
    sent_to=models.ForeignKey('LOGIN.NewUser',on_delete=models.CASCADE)
    class Meta:
        unique_together=['blog','sent_to']

class FollowUnNotification(models.Model):
    content=models.TextField()
    read=models.BooleanField(default=False,db_index=True)
    owner=models.ForeignKey('LOGIN.NewUser',on_delete=models.CASCADE)
    user=models.ForeignKey('LOGIN.NewUser',on_delete=models.CASCADE,related_name='user_follow_notification')
    


class Comments(models.Model):
    text=models.TextField()
    owner=models.ForeignKey('LOGIN.NewUser',on_delete=models.CASCADE)
    blog=models.ForeignKey(Blog,on_delete=models.CASCADE)


class Streak(models.Model):
    user_streak=models.OneToOneField('LOGIN.NewUser',on_delete=models.CASCADE)
    count=models.IntegerField(default=0,db_index=True)
    last_activity_date=models.DateTimeField(null=True,blank=True)
    max_streak=models.IntegerField(default=0,db_index=True)