from django import forms

from .models import Comment, Post


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Текст комментария'
        }
        help_texts = {
            'text': 'Текст нового комментария'
        }
        error_messages = {
            'text': {
                'required': 'поле должно быть заполнено',
            }
        }


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group', 'image',)
        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
            'image': 'Картинка'
        }
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
            'image': 'Картинка поста'
        }
        error_messages = {
            'text': {
                'required': 'поле должно быть заполнено',
            }
        }
