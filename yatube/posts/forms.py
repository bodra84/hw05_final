from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Форма создания нового поста."""

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        help_texts = {'text': 'Текст нового поста',
                      'group': 'Выберите группу поста или оставьте поле пустым'
                      }


class CommentForm(forms.ModelForm):
    """Форма создания нового поста."""

    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {'text': 'Текст комментария'}

