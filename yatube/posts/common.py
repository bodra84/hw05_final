from django.conf import settings
from django.core.paginator import Paginator


def page_list(request, post_list):
    """Функция page_list возвращает список постов, разбитый постранично,
    с количеством постов на странице, равным константе COUNT_OF_POSTS."""
    paginator = Paginator(post_list, settings.COUNT_OF_POSTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
