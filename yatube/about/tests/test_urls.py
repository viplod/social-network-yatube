from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        self.templates_url_names_for_guest_client = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        self.guest_client = Client()

    def test_url_exist_for_guest_client(self):
        for adress, template in (
            self.templates_url_names_for_guest_client.items()
        ):
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, 200)

    def test_url_correct_templates(self):
        templates = self.templates_url_names_for_guest_client
        for adress, template in templates.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)
