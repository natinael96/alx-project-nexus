"""
Unit tests for accounts app - Authentication and User Management.
"""
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.models import User

User = get_user_model()


class TestUserRegistration:
    """Tests for user registration endpoint."""
    
    def test_register_user_success(self, api_client):
        """Test successful user registration."""
        url = reverse('accounts:register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'user'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username='newuser').exists()
        assert 'password' not in response.data
    
    def test_register_user_password_mismatch(self, api_client):
        """Test registration with mismatched passwords."""
        url = reverse('accounts:register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password2': 'DifferentPass123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data
    
    def test_register_user_weak_password(self, api_client):
        """Test registration with weak password."""
        url = reverse('accounts:register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': '123',
            'password2': '123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_user_duplicate_email(self, api_client, user):
        """Test registration with duplicate email."""
        url = reverse('accounts:register')
        data = {
            'username': 'differentuser',
            'email': user.email,
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
    
    def test_register_user_as_admin_blocked(self, api_client):
        """Test that users cannot register as admin."""
        url = reverse('accounts:register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'admin'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'role' in response.data


class TestUserLogin:
    """Tests for user login endpoint."""
    
    def test_login_with_username_success(self, api_client, user):
        """Test login with username."""
        url = reverse('accounts:login')
        data = {
            'username': user.username,
            'password': 'testpass123'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
    
    def test_login_with_email_success(self, api_client, user):
        """Test login with email address."""
        url = reverse('accounts:login')
        data = {
            'username': user.email,
            'password': 'testpass123'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
    
    def test_login_invalid_credentials(self, api_client, user):
        """Test login with invalid credentials."""
        url = reverse('accounts:login')
        data = {
            'username': user.username,
            'password': 'wrongpassword'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_inactive_user(self, api_client, user):
        """Test login with inactive user."""
        user.is_active = False
        user.save()
        url = reverse('accounts:login')
        data = {
            'username': user.username,
            'password': 'testpass123'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestTokenRefresh:
    """Tests for token refresh endpoint."""
    
    def test_refresh_token_success(self, api_client, user):
        """Test successful token refresh."""
        refresh = RefreshToken.for_user(user)
        url = reverse('accounts:refresh')
        data = {'refresh': str(refresh)}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
    
    def test_refresh_token_invalid(self, api_client):
        """Test refresh with invalid token."""
        url = reverse('accounts:refresh')
        data = {'refresh': 'invalid_token'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetCurrentUser:
    """Tests for get current user endpoint."""
    
    def test_get_current_user_authenticated(self, authenticated_client, user):
        """Test getting current user when authenticated."""
        url = reverse('accounts:current-user')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == user.id
        assert response.data['username'] == user.username
    
    def test_get_current_user_unauthenticated(self, api_client):
        """Test getting current user when not authenticated."""
        url = reverse('accounts:current-user')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateCurrentUser:
    """Tests for update current user endpoint."""
    
    def test_update_current_user_success(self, authenticated_client, user):
        """Test successful user profile update."""
        url = reverse('accounts:update-user')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'bio': 'Updated bio'
        }
        response = authenticated_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.first_name == 'Updated'
        assert user.bio == 'Updated bio'
    
    def test_update_current_user_role_blocked(self, authenticated_client, user):
        """Test that users cannot change their own role."""
        url = reverse('accounts:update-user')
        data = {'role': 'admin'}
        response = authenticated_client.patch(url, data, format='json')
        # Should either ignore or reject role change
        user.refresh_from_db()
        assert user.role != 'admin'


class TestChangePassword:
    """Tests for change password endpoint."""
    
    def test_change_password_success(self, authenticated_client, user):
        """Test successful password change."""
        url = reverse('accounts:change-password')
        data = {
            'old_password': 'testpass123',
            'new_password': 'NewSecurePass123!',
            'new_password2': 'NewSecurePass123!'
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password('NewSecurePass123!')
    
    def test_change_password_wrong_old_password(self, authenticated_client, user):
        """Test password change with wrong old password."""
        url = reverse('accounts:change-password')
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'NewSecurePass123!',
            'new_password2': 'NewSecurePass123!'
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_change_password_mismatch(self, authenticated_client, user):
        """Test password change with mismatched new passwords."""
        url = reverse('accounts:change-password')
        data = {
            'old_password': 'testpass123',
            'new_password': 'NewSecurePass123!',
            'new_password2': 'DifferentPass123!'
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestUserManagementAdmin:
    """Tests for admin-only user management endpoints."""
    
    def test_list_users_admin_only(self, admin_client):
        """Test that only admins can list users."""
        url = reverse('accounts:user-list')
        response = admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_list_users_non_admin_forbidden(self, authenticated_client):
        """Test that non-admins cannot list users."""
        url = reverse('accounts:user-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_list_users_filter_by_role(self, admin_client, user, employer, admin_user):
        """Test filtering users by role."""
        url = reverse('accounts:user-list')
        response = admin_client.get(url, {'role': 'user'})
        assert response.status_code == status.HTTP_200_OK
        assert all(u['role'] == 'user' for u in response.data['results'])
    
    def test_list_users_search(self, admin_client, user):
        """Test searching users."""
        url = reverse('accounts:user-list')
        response = admin_client.get(url, {'search': user.username})
        assert response.status_code == status.HTTP_200_OK
        assert any(u['username'] == user.username for u in response.data['results'])
    
    def test_get_user_detail_admin(self, admin_client, user):
        """Test admin getting user details."""
        url = reverse('accounts:user-detail', kwargs={'pk': user.pk})
        response = admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == user.id
    
    def test_update_user_admin(self, admin_client, user):
        """Test admin updating user."""
        url = reverse('accounts:user-detail', kwargs={'pk': user.pk})
        data = {'first_name': 'Updated', 'is_active': False}
        response = admin_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.first_name == 'Updated'
        assert not user.is_active
    
    def test_delete_user_admin(self, admin_client, user):
        """Test admin deleting user."""
        url = reverse('accounts:user-detail', kwargs={'pk': user.pk})
        response = admin_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(pk=user.pk).exists()
    
    def test_admin_cannot_delete_self(self, admin_client, admin_user):
        """Test that admin cannot delete themselves."""
        url = reverse('user-detail', kwargs={'pk': admin_user.pk})
        response = admin_client.delete(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
