import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, Comment

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
            image=uploaded
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk,
            'image': self.post.image,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': self.user
        }))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=self.group,
                text='Тестовый текст',
                image='posts/small.gif',
            ).exists()
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        form_data = {
            'text': 'Новый тестовый текст',
            'group': self.group.pk
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={
                'post_id': self.post.pk
            }),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
            'post_id': self.post.pk
        }))
        self.assertTrue(
            Post.objects.filter(
                group=self.group,
                text='Новый тестовый текст'
            ).exists()
        )

    def test_create_post_guest_client(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(response, ('/auth/login/?next=/create/'))

    def test_create_comment(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий',
            'author': self.user,
            'post': self.post,
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={
                'post_id': self.post.pk,
            }),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
            'post_id': self.post.pk
        }))
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                author=self.user,
                text='Тестовый комментарий',
                post=self.post,
            ).exists()
        )
