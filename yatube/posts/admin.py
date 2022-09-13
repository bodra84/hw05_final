from django.contrib import admin

from .models import Comment, Follow, Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Класс PostAdmin используется для отображения
    и изменения свойств модели post.
    """
    list_display = ('pk', 'text', 'pub_date', 'author', 'group', 'image',)
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """Класс GroupAdmin используется для отображения
    и изменения свойств модели Group.
    """
    list_display = ('title', 'slug', 'description',)
    search_fields = ('title', 'slug',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Класс CommentAdmin используется для отображения
    и изменения свойств модели Comment.
    """
    list_display = ('post', 'author', 'text', 'created',)
    search_fields = ('post', 'text', 'author',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Класс FollowAdmin используется для отображения
    и изменения свойств модели Follow.
    """
    list_display = ('user', 'author',)
    search_fields = ('user', 'author',)
    empty_value_display = '-пусто-'
