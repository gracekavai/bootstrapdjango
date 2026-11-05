from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from myapp.models import ContactMessage


class PageNavigationTests(TestCase):
    def test_main_pages_render(self):
        for url in (
            '/',
            '/properties/',
            '/contact/',
            '/property-details/',
            '/about/',
            '/login/',
            '/register/',
        ):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_property_prices_have_currency_selector(self):
        response = self.client.get('/properties/')

        self.assertContains(response, 'data-currency-select')
        self.assertContains(response, 'data-price-usd="2264000"')
        self.assertContains(response, 'value="KES"')
        self.assertContains(response, 'value="USD"')
        self.assertContains(response, 'value="EUR"')

    def test_contact_page_has_social_and_whatsapp_links(self):
        response = self.client.get('/contact/')

        self.assertContains(response, 'https://www.instagram.com/pixelvillas')
        self.assertContains(response, 'https://www.facebook.com/pixelvillas')
        self.assertContains(response, 'https://www.tiktok.com/@pixelvillas')
        self.assertContains(response, 'https://wa.me/254717474397')

    def test_registration_page_loads_pixelvillas_styles(self):
        response = self.client.get(reverse('register'))

        self.assertContains(response, '/static/css/pixelvillas.css')
        self.assertContains(response, 'class="auth-card"')


class AuthenticationTests(TestCase):
    def test_registration_creates_user_and_redirects_to_login(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'newuser',
                'password1': 'ValidPass!928',
                'password2': 'ValidPass!928',
            },
        )
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_can_log_in_and_log_out(self):
        User.objects.create_user(username='member', password='ValidPass!928')

        response = self.client.post(
            reverse('login'),
            {'username': 'member', 'password': 'ValidPass!928'},
        )
        self.assertRedirects(response, reverse('index'))
        self.assertTrue('_auth_user_id' in self.client.session)

        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('index'))
        self.assertNotIn('_auth_user_id', self.client.session)


class ContactFormTests(TestCase):
    def test_valid_contact_submission_is_saved_and_confirms(self):
        csrf_client = self.client_class(enforce_csrf_checks=True)
        response = csrf_client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)

        csrf_token = response.cookies['csrftoken'].value
        response = csrf_client.post(
            reverse('contact'),
            {
                'name': 'Grace Kavai',
                'email': 'grace@example.com',
                'subject': 'Viewing request',
                'message': 'I would like to arrange a viewing.',
                'csrfmiddlewaretoken': csrf_token,
            },
        )

        self.assertRedirects(response, reverse('contact'))
        self.assertEqual(ContactMessage.objects.count(), 1)

        response = csrf_client.get(reverse('contact'))
        self.assertContains(response, 'Submitted. Please await feedback.')

    def test_contact_submission_requires_csrf_token(self):
        csrf_client = self.client_class(enforce_csrf_checks=True)
        response = csrf_client.post(
            reverse('contact'),
            {
                'name': 'Grace Kavai',
                'email': 'grace@example.com',
                'message': 'A message without a CSRF token.',
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_invalid_contact_submission_is_not_saved(self):
        response = self.client.post(
            reverse('contact'),
            {
                'name': 'Grace Kavai',
                'email': 'not-an-email',
                'message': 'Please contact me.',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter a valid email address.')
        self.assertEqual(ContactMessage.objects.count(), 0)
