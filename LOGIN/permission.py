from rest_framework.permissions import BasePermission
from LOGIN.models import UserFollowing
from BLOG.models import OrganizationFollowing


class is_temp_pass(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_password_temp==True and request.user.role=='E')
    
class Founder_Set_Up(BasePermission):
    def has_permission(self, request, view):
        return (request.user.role=='F' and request.user.is_verified==True and request.user.created_organization==True)
    

class is_Founder(BasePermission):
    def has_permission(self, request, view):
        return (request.user.role=='F' and request.user.is_verified==True and request.user.created_organization==False)
    

class BlogCreater(BasePermission):
    def has_permission(self, request, view):
        if request.user.role=='F':
            return (request.user.created_organization==True and request.user.is_verified==True)
        else:
            return (request.user.is_password_temp==False)
        

class SameOrganizatoin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.organization==obj and request.user.role=='F'
    

class followPermissions(BasePermission):
    def has_object_permission(self, request, view, obj):
        user=request.user
        if user.role=='F':
            following=UserFollowing.objects.select_related('following').filter(user_id=user.id).values_list('following__Name',flat=True)
            if obj.Name not in following:
                if obj.id!=user.organization_id:
                    return user.is_verified==True and user.created_organization==True 
        elif user.role=='E':
            following=UserFollowing.objects.select_related('following').filter(user_id=user.id).values_list('following__Name',flat=True)
            organizationfollowing=OrganizationFollowing.objects.select_related('following').filter(organization_id=request.user.organization_id).values_list('following__Name',flat=True)
            if obj.Name not in following or obj.Name in organizationfollowing:
                if obj.id!=user.organization_id:
                    return user.is_password_temp==False 
        return False



class unfollowPermissions(BasePermission):
    def has_object_permission(self, request, view, obj):
        user=request.user
        if user.role=='F':
            following=UserFollowing.objects.select_related('following').filter(user_id=user.id).values_list('following__Name',flat=True)
            if obj.Name in following:
                return user.is_verified==True and user.created_organization==True 
        elif user.role=='E':
            organizationfollowing=OrganizationFollowing.objects.select_related('following').filter(organization_id=request.user.organization_id).values_list('following__Name',flat=True)
            following=UserFollowing.objects.select_related('following').filter(user_id=user.id).values_list('following__Name',flat=True)
            if obj.Name in following or obj.Name in organizationfollowing:
                return user.is_password_temp==False 
        return False

class BlogReadPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.organization.type=='Pvt':
            following=UserFollowing.objects.select_related('following').filter(user_id=request.user.id).values_list('following__Name',flat=True)
            organizationfollowing=OrganizationFollowing.objects.select_related('following').filter(organization_id=request.user.organization_id).values_list('following__Name',flat=True)
            if request.user.organization==obj.organization:
                return True
            elif obj.organization.Name in following:
                return True
            elif obj.organization.Name in organizationfollowing :
                return True
            else:
                return False
        elif obj.organization.type=='Pub':
            return True
        else:
            return False
        

class BlogUpdatePermissions(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.id == obj.created_by_id
    


class BlogDeletePermissions(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.id == obj.created_by_id or obj.organization.founder_id==request.user.id
    

class CommentsUpdatePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.id==obj.owner_id or obj.blog.organization.founder_id==request.user.id
    
class employeeDeletePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.organization_id==obj.organization_id and request.user.role=='F' and request.user!=obj:
            return True
        return False
        
class delete_pin_permissions(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.organization_id==obj.blog.organization_id and request.user.role=='F':
            return True
        return False
