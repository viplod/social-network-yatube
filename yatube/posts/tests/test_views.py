import shutil
import tempfile

from django.core.cache import cache
from django import forms
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Follow, Group, Post
from posts.forms import PostForm

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTest(TestCase):
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
        cls.follower = User.objects.create_user(username='HasNoName')
        cls.follower_tempname = User.objects.create_user(username='tempname')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,

            image=uploaded
        )
        cls.follow = Follow.objects.create(
            user=cls.follower,
            author=cls.user
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.hasnoname_user = Client()
        self.hasnoname_user.force_login(self.follower)
        self.tempname_user = Client()
        self.tempname_user.force_login(self.follower_tempname)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_cache(self):
        response_before_del = self.authorized_client.get(
            reverse('posts:index')
        )
        Post.objects.get(pk=self.post.pk).delete()
        response_after_del = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertEqual(
            response_before_del.content, response_after_del.content
        )
        cache.clear()
        response_after_clear_cache = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertNotEqual(
            response_after_clear_cache.content, response_after_del.content
        )

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={
                'slug': 'test-slug'
            }): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': self.user
            }): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': self.post.pk
            }): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={
                'post_id': self.post.pk
            }): 'posts/create_post.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        data_for_test = {
            first_object.text: 'Тестовый пост',
            first_object.author: self.user,
            first_object.group: self.group,
            first_object.image: self.post.image,
        }
        for obj_elem, data in data_for_test.items():
            with self.subTest(obj_elem=obj_elem):
                self.assertEqual(obj_elem, data)

    def test_group_list_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={
                'slug': 'test-slug'
            }))
        first_object = response.context['page_obj'][0]
        group_context = response.context['group']
        data_for_test = {
            first_object.text: 'Тестовый пост',
            first_object.author: self.user,
            first_object.group: self.group,
            first_object.image: self.post.image,
            group_context: self.group,
        }
        for obj_elem, data in data_for_test.items():
            with self.subTest(obj_elem=obj_elem):
                self.assertEqual(obj_elem, data)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={
                'username': self.user
            }))
        first_object = response.context['page_obj'][0]
        username_context = response.context['author']
        count_context = response.context['count']
        self.assertIsInstance(count_context, int)
        data_for_test = {
            first_object.text: 'Тестовый пост',
            first_object.author: self.user,
            first_object.group: self.group,
            first_object.image: self.post.image,
            username_context: self.user,
        }
        for obj_elem, data in data_for_test.items():
            with self.subTest(obj_elem=obj_elem):
                self.assertEqual(obj_elem, data)

    def test_post_detail_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={
                'post_id': self.post.pk
            }))
        first_object = response.context['post']
        count_context = response.context['count']
        self.assertIsInstance(count_context, int)
        data_for_test = {
            first_object.text: 'Тестовый пост',
            first_object.author: self.user,
            first_object.group: self.group,
            first_object.image: self.post.image,
        }
        for obj_elem, data in data_for_test.items():
            with self.subTest(obj_elem=obj_elem):
                self.assertEqual(obj_elem, data)

    def test_post_create_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        is_edit_context = response.context['is_edit']
        self.assertIsInstance(is_edit_context, bool)
        self.assertFalse(is_edit_context, 'not False')
        form_context = response.context['form']
        self.assertIsInstance(form_context, PostForm)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={
                'post_id': self.post.pk
            }))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        is_edit_context = response.context['is_edit']
        self.assertIsInstance(is_edit_context, bool)
        self.assertTrue(is_edit_context, 'not True')
        form_context = response.context['form']
        self.assertIsInstance(form_context, PostForm)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        first_object = response.context['post']

        data_for_test = {
            first_object.text: 'Тестовый пост',
            first_object.author: self.user,
            first_object.group: self.group,
        }
        for obj_elem, data in data_for_test.items():
            with self.subTest(obj_elem=obj_elem):
                self.assertEqual(obj_elem, data)

    def test_folliwing_to_author(self):
        response = self.tempname_user.get(reverse(
            'posts:follow_index',
        ))
        count_before_following = len(response.context['page_obj'])
        response = self.tempname_user.get(reverse(
            'posts:profile_follow', kwargs={
                'username': self.user,
            }))
        response = self.tempname_user.get(reverse(
            'posts:follow_index',
        ))
        count_after_following = len(response.context['page_obj'])
        self.assertEqual(count_before_following + 1, count_after_following)

    def test_unfolliwing_from_author(self):
        response = self.tempname_user.get(reverse(
            'posts:profile_follow', kwargs={
                'username': self.user,
            }))
        response = self.tempname_user.get(reverse(
            'posts:follow_index',
        ))
        count_before_unfollowing = len(response.context['page_obj'])
        self.assertEqual(count_before_unfollowing, 1)
        response = self.tempname_user.get(reverse(
            'posts:profile_unfollow', kwargs={
                'username': self.user,
            }))
        response = self.tempname_user.get(reverse(
            'posts:follow_index',
        ))
        count_after_unfollowing = len(response.context['page_obj'])
        self.assertEqual(count_after_unfollowing, count_before_unfollowing - 1)

    def test_view_post_following_author(self):
        response = self.hasnoname_user.get(reverse(
            'posts:follow_index',
        ))
        count_before_create_post = len(response.context['page_obj'])
        form_data = {
            'text': 'Тестовый текст для подписчиков',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        response = self.hasnoname_user.get(reverse(
            'posts:follow_index',
        ))
        count_after_create_post = len(response.context['page_obj'])
        self.assertNotEqual(count_before_create_post, count_after_create_post)

    def test_view_post_notfollowing_author(self):
        response = self.authorized_client.get(reverse(
            'posts:follow_index',
        ))
        count_before_create_post = len(response.context['page_obj'])
        form_data = {
            'text': 'Тестовый текст для подписчиков',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        response = self.authorized_client.get(reverse(
            'posts:follow_index',
        ))
        count_after_create_post = len(response.context['page_obj'])
        self.assertEqual(count_before_create_post, count_after_create_post)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        obj_posts = list()
        num_post = 13
        for _ in range(num_post):
            obj_posts.append(Post(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group,
            ))
        Post.objects.bulk_create(obj_posts)

    def setUp(self):
        self.client = Client()
        self.url_pages_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={
                'slug': 'test-slug'
            }),
            reverse('posts:profile', kwargs={
                'username': self.user
            }),
        ]

    def test_paginator_one_page_ten_records(self):
        for item in self.url_pages_names:
            with self.subTest(item=item):
                response = self.client.get(item)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_paginator_second_page_three_records(self):
        paginator_page_2 = {'page': 2}
        for item in self.url_pages_names:
            with self.subTest(item=item):
                response = self.client.get(item, paginator_page_2)
                self.assertEqual(len(response.context['page_obj']), 3)
