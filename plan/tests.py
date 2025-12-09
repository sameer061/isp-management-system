from django.test import TestCase, Client
from django.contrib.auth.models import User
from plan.models import Plan, Userprofile
from django.urls import reverse

class UpdateUserTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='password')
        self.client.login(username='admin', password='password')

        self.plan = Plan.objects.create(plan_name='Basic', cost=100)
        self.user_profile = Userprofile.objects.create(
            user='user1',
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phoneno='+911234567890',
            current_plan=self.plan
        )
        self.user_profile_digit = Userprofile.objects.create(
            user='123',
            first_name='Jane',
            last_name='Doe',
            email='jane@example.com',
            phoneno='+910987654321',
            current_plan=self.plan
        )

    def test_update_user_url(self):
        # This works fine
        url = reverse('updateuser', args=[self.user_profile.user])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_user_url_with_digits(self):
        # This fails before fix because reverse resolves to /123/ which matches update_plan
        url = reverse('updateuser', args=[self.user_profile_digit.user])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Verify we are on the correct page (not update plan)
        # plan/templates/update-user.html likely contains "Update User" or similar text
        # plan/templates/update-plan.html likely contains "Update Plan"
        # Let's just check status code for now, as failure is 500 or 404 (Plan not found)

    def test_update_plan_url(self):
        # Verify update plan still works
        url = reverse('updateplan', args=[self.plan.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
