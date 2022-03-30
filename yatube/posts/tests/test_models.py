from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Follow, Group, Post, Comment

User = get_user_model()


class PostModelTest(TestCase):
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
            text='Тестовый пост должен быть длиннее 15 символов',
        )

    def setUp(self):
        self.field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        self.field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
            'image': 'Картинка',
        }

    def test_models_have_correct_object_name_post(self):
        post = PostModelTest.post
        self.assertEqual(post.text[:15], str(post))

    def test_models_have_correct_object_name_group(self):
        group = PostModelTest.group
        self.assertEqual(group.title, str(group))

    def test_verbose_name(self):
        post = PostModelTest.post
        for field, expected_value in self.field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
        post = PostModelTest.post
        for field, expected_value in self.field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

    def setUp(self):
        self.field_help_texts = {
            'title': 'Введите название группы',
            'slug': 'Название группы латиницей',
            'description': 'Напишите о чем группа',
        }
        self.field_verboses = {
            'title': 'Название группы',
            'slug': 'Slug',
            'description': 'Описание группы',
        }

    def test_models_have_correct_object_name_group(self):
        group = GroupModelTest.group
        self.assertEqual(group.title, str(group))

    def test_verbose_name(self):
        group = GroupModelTest.group
        for field, expected_value in self.field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
        group = GroupModelTest.group
        for field, expected_value in self.field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value)


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост должен быть длиннее 15 символов',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Текст комментария должен быть длиннее 15 символов',
        )

    def setUp(self):
        self.field_help_texts = {
            'text': 'Введите текст комментария',
        }
        self.field_verboses = {
            'post': 'Пост',
            'author': 'Автор',
            'text': 'Текст комментария',
            'created': 'Дата публикации',
        }

    def test_models_have_correct_object_title_comment(self):
        comment = CommentModelTest.comment
        self.assertEqual(comment.text[:15], str(comment))

    def test_verbose_name(self):
        comment = CommentModelTest.comment
        for field, expected_value in self.field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(
                        field
                    ).verbose_name, expected_value)

    def test_help_text(self):
        comment = CommentModelTest.comment
        for field, expected_value in self.field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).help_text, expected_value)


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.author = User.objects.create_user(username='author')
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author,
        )

    def setUp(self):
        self.field_verboses = {
            'user': 'Подписчик',
            'author': 'Автор',
        }

    def test_verbose_name(self):
        follow = FollowModelTest.follow
        for field, expected_value in self.field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    follow._meta.get_field(
                        field
                    ).verbose_name, expected_value)
