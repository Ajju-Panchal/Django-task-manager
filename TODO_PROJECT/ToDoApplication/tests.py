from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Task, UserProfile


class RegistrationTests(TestCase):
    def test_registration_creates_user_and_profile(self):
        response = self.client.post(reverse("register"), {
            "username": "sam", "email": "sam@example.com", "phone": "1234567890",
            "password": "StrongPass123!", "password1": "StrongPass123!",
        })
        self.assertRedirects(response, reverse("index"))
        user = User.objects.get(username="sam")
        self.assertTrue(UserProfile.objects.filter(user=user, phone="1234567890").exists())
        self.assertTrue(self.client.session.get("_auth_user_id"))

    def test_registration_rejects_mismatched_passwords(self):
        response = self.client.post(reverse("register"), {
            "username": "sam", "email": "sam@example.com", "phone": "1234567890",
            "password": "one", "password1": "two",
        })
        self.assertRedirects(response, reverse("register"))
        self.assertFalse(User.objects.filter(username="sam").exists())


class TaskAccessTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="test-password-123")
        self.other = User.objects.create_user(username="other", password="test-password-123")
        self.task = Task.objects.create(user=self.owner, task_title="Private task")

    def test_task_api_requires_login(self):
        response = self.client.get(reverse("get_task_list"))
        self.assertEqual(response.status_code, 302)

    def test_task_list_contains_only_current_users_tasks(self):
        self.client.force_login(self.other)
        response = self.client.get(reverse("get_task_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["tasks"], [])

    def test_other_user_cannot_read_edit_or_delete_task(self):
        self.client.force_login(self.other)
        detail_url = reverse("get_or_edit_task", args=[self.task.id])
        delete_url = reverse("delete_task", args=[self.task.id])
        self.assertEqual(self.client.get(detail_url).status_code, 404)
        self.assertEqual(self.client.post(detail_url, {"title": "Stolen", "priority": "1", "status": "pending"}).status_code, 404)
        self.assertEqual(self.client.post(delete_url).status_code, 404)
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())

    def test_create_and_update_validate_task_fields(self):
        self.client.force_login(self.owner)
        create = self.client.post(reverse("add_task"), {"title": "New", "priority": "2"})
        self.assertEqual(create.status_code, 201)
        task = Task.objects.get(task_title="New")
        update = self.client.post(reverse("get_or_edit_task", args=[task.id]), {
            "title": "Updated", "description": "Details", "priority": "1", "status": "completed",
        })
        self.assertEqual(update.status_code, 200)
        task.refresh_from_db()
        self.assertEqual(task.task_title, "Updated")
        self.assertEqual(task.task_status, "completed")
        invalid = self.client.post(reverse("add_task"), {"title": "Bad", "priority": "99"})
        self.assertEqual(invalid.status_code, 400)
