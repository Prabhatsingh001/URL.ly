from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import UrlModel, UrlVisit

User = get_user_model()


class UrlModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpass"
        )
        self.url = UrlModel.objects.create(
            original_url="https://www.example.com",
            user=self.user,
            expires_at=timezone.now() + timedelta(days=7),
        )
        self.url.short_url = "short1234"
        self.url.save()

    def test_url_str(self):
        self.assertEqual(str(self.url), "short1234")

    def test_url_expiry(self):
        if self.url.expires_at is not None:
            self.assertTrue(self.url.expires_at > timezone.now())

    def test_url_unique(self):
        with self.assertRaises(Exception):
            UrlModel.objects.create(
                original_url="https://www.example.com",
                user=self.user,
            )


class UrlVisitTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser2", email="testuser2@example.com", password="testpass"
        )
        self.url = UrlModel.objects.create(
            original_url="https://www.test.com",
            user=self.user,
        )
        self.visit = UrlVisit.objects.create(
            url=self.url,
            ip_address="127.0.0.1",
            browser="Chrome",
            os="Windows",
            device="PC",
        )

    def test_visit_created(self):
        self.assertEqual(self.url.visits.count(), 1)  # type: ignore
        self.assertEqual(self.visit.url, self.url)


class UrlLogicViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="viewuser", email="viewuser@example.com", password="viewpass"
        )
        self.client.login(username="viewuser", password="viewpass")
        self.url = UrlModel.objects.create(
            original_url="https://www.logic.com",
            user=self.user,
            expires_at=timezone.now() + timedelta(days=7),
        )
        self.url.short_url = "logic123"
        self.url.save()

    def test_make_short_url(self):
        response = self.client.post(
            reverse("url:make_short_url"),
            {
                "long_url": "https://www.newsite.com",
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirect to home

    def test_redirect_url(self):
        response = self.client.get(
            reverse("url:redirect_url", args=[self.url.short_url])
        )
        # Should redirect to original_url or show expired/404
        self.assertIn(response.status_code, [302, 200])

    def test_delete_url(self):
        response = self.client.post(
            reverse("url:delete_url", args=[self.url.pk]), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(UrlModel.objects.filter(pk=self.url.pk).exists())

    def test_update_url(self):
        response = self.client.post(
            reverse("url:edit_url", args=[self.url.pk]),
            {
                "long_url": "https://www.updated.com",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.url.refresh_from_db()
        self.assertEqual(self.url.original_url, "https://www.updated.com")
