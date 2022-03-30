from django.utils.translation import gettext_lazy as _
from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': _('Текст поста'),
            'group': _('Название группы'),
            'image': _('Картинка'),
        }
        help_texts = {
            'text': _('Введите текст поста'),
            'group': _('Выберите к какой группе относиться пост'),
            'image': _('Добавьте картинку к посту'),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': _('Текст комментария'),
        }
        help_texts = {
            'text': _('Введите текст комментария'),
        }
