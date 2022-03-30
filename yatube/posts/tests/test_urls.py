from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.templates_url_names_for_guest_client = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
        }

        self.templates_url_names_authorized_client = {
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }

        self.guest_client = Client()
        hasnoname_user = User.objects.create_user(username='HasNoName')
        self.hasnoname_user = Client()
        self.hasnoname_user.force_login(hasnoname_user)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_url_exist_for_guest_client(self):
        for adress, template in (
            self.templates_url_names_for_guest_client.items()
        ):
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, 200)

    def test_url_correct_templates(self):
        templates = self.templates_url_names_for_guest_client.copy()
        templates.update(self.templates_url_names_authorized_client)
        for adress, template in templates.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_url_exist_for_authorized_client(self):
        for adress, template in (
            self.templates_url_names_authorized_client.items()
        ):
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertEqual(response.status_code, 200)

    def test_url_unexist(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_url_create_for_anonymous_client(self):
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/create/'))

    def test_url_post_edit_for_not_author(self):
        response = self.hasnoname_user.get('/posts/1/edit/')
        self.assertRedirects(
            response, ('/posts/1/'))

    def test_url_post_edit_for_anonymous_client(self):
        response = self.hasnoname_user.get('/posts/1/edit/')
        self.assertRedirects(response, ('/posts/1/'))

    def test_url_comment_for_anonymous_client(self):
        response = self.guest_client.get('/posts/1/comment/')
        self.assertRedirects(
            response, ('/auth/login/?next=/posts/1/comment/'))

    def test_url_comment_for_authorized_client(self):
        response = self.authorized_client.get('/posts/1/comment/')
        self.assertRedirects(response, ('/posts/1/'))

    def test_url_follow_for_anonymous_client(self):
        response = self.guest_client.get('/follow/', follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/follow/'))
