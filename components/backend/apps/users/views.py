"""
Views for users app
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout
from django.utils import timezone

from .models import User, Organization, UserProfile
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    OrganizationSerializer, LoginSerializer, ChangePasswordSerializer
)


class LoginView(APIView):
    """User login view"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Update last activity
        user.last_activity = timezone.now()
        user.save(update_fields=['last_activity'])
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


class LogoutView(APIView):
    """User logout view"""
    
    def post(self, request):
        logout(request)
        return Response({'detail': 'Successfully logged out.'})


class RegisterView(APIView):
    """User registration view"""
    permission_classes = [permissions.AllowAny]  # Change in production
    
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    """User CRUD operations"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['role', 'is_active', 'organization']
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'email', 'last_activity']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_queryset(self):
        """Filter users by organization for non-admins"""
        user = self.request.user
        queryset = User.objects.select_related('organization', 'profile')
        
        # Admin sees all users
        if user.role == User.Role.ADMIN:
            return queryset
        
        # Others see only users from their organization
        if user.organization:
            return queryset.filter(organization=user.organization)
        
        return queryset.filter(id=user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update current user profile"""
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=request.method == 'PATCH'
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change user password"""
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        # Check old password
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'old_password': 'Wrong password.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'detail': 'Password updated successfully.'})
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate user"""
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'detail': 'User activated.'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate user"""
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'detail': 'User deactivated.'})


class OrganizationViewSet(viewsets.ModelViewSet):
    """Organization CRUD operations"""
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['is_active']
    search_fields = ['name', 'email']
    ordering_fields = ['created_at', 'name']
    
    def get_queryset(self):
        """Admin sees all, others see only their organization"""
        user = self.request.user
        queryset = Organization.objects.all()
        
        if user.role == User.Role.ADMIN:
            return queryset
        
        if user.organization:
            return queryset.filter(id=user.organization.id)
        
        return queryset.none()
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """Get users of an organization"""
        organization = self.get_object()
        users = User.objects.filter(organization=organization)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get organization statistics"""
        organization = self.get_object()
        
        stats = {
            'total_users': organization.users.count(),
            'active_users': organization.users.filter(is_active=True).count(),
            'agents': organization.users.filter(role=User.Role.AGENT).count(),
            'supervisors': organization.users.filter(role=User.Role.SUPERVISOR).count(),
            'managers': organization.users.filter(role=User.Role.MANAGER).count(),
        }
        
        return Response(stats)
