from django.test import Client, TestCase
from django.urls import reverse

from .models import Contact, CustomUser, UserProfile


class CustomUserModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test@example.com", username="testuser", password="testpass123"
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, "test@example.com")
        self.assertFalse(self.user.is_active)  # By default
        self.assertTrue(CustomUser.objects.filter(email="test@example.com").exists())


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="profile@example.com", username="profileuser", password="testpass123"
        )
        self.profile = UserProfile.objects.get(user=self.user)

    def test_profile_created(self):
        self.assertEqual(self.profile.user, self.user)


class ContactModelTest(TestCase):
    def test_contact_creation(self):
        contact = Contact.objects.create(
            name="John Doe", email="john@example.com", message="Hello!"
        )
        self.assertEqual(contact.name, "John Doe")
        self.assertEqual(contact.email, "john@example.com")


class AuthViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse("a:signup")
        self.login_url = reverse("a:login")
        self.contact_url = reverse("a:contact")

    def test_signup_view_get(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)

    def test_signup_view_post(self):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "testpass123",
            "confirm-password": "testpass123",
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after signup
        self.assertTrue(CustomUser.objects.filter(email="newuser@example.com").exists())

    def test_login_view_get(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)

    def test_contact_view_post(self):
        data = {
            "name": "Test User",
            "email": "testuser@example.com",
            "message": "Hello!",
        }
        response = self.client.post(self.contact_url, data)
        self.assertIn(response.status_code, [200, 302])
        self.assertTrue(Contact.objects.filter(email="testuser@example.com").exists())
