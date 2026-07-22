from rest_framework.test import APITestCase

from core.models import User


def register(client, role="student", username="u1", **extra):
    payload = {
        "role": role,
        "username": username,
        "password": "Str0ngPass!23",
        "password2": "Str0ngPass!23",
        "first_name": "Test",
        "last_name": "User",
        "email": f"{username}@example.com",
    }
    if role == "teacher":
        payload.update({"department": "CS", "designation": "Lecturer"})
    else:
        payload.update({"university": "State U", "department": "CS"})
    payload.update(extra)
    return client.post("/api/auth/register/", payload)


class AuthTests(APITestCase):
    def test_register_student_creates_profile_and_logs_in(self):
        resp = register(self.client, role="student", username="stud")
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(resp.data["role"], "student")
        user = User.objects.get(username="stud")
        self.assertTrue(user.is_student)
        self.assertTrue(hasattr(user, "student"))
        # session is active -> /me works
        me = self.client.get("/api/auth/me/")
        self.assertEqual(me.status_code, 200)

    def test_register_teacher_requires_department(self):
        resp = self.client.post(
            "/api/auth/register/",
            {
                "role": "teacher", "username": "t", "password": "Str0ngPass!23",
                "password2": "Str0ngPass!23", "first_name": "A", "last_name": "B",
                "email": "t@example.com",
            },
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("department", resp.data)

    def test_password_mismatch_rejected(self):
        resp = register(self.client, username="mm", password2="different")
        self.assertEqual(resp.status_code, 400)

    def test_login_logout(self):
        register(self.client, role="teacher", username="teach")
        self.client.post("/api/auth/logout/")
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 403)
        resp = self.client.post(
            "/api/auth/login/", {"username": "teach", "password": "Str0ngPass!23"}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["role"], "teacher")

    def test_me_requires_auth(self):
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 403)
