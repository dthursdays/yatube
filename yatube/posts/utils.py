from typing import List, Tuple, Union

from django.core.paginator import Page, Paginator
from django.db.models import QuerySet

from yatube.settings import POSTS_ON_PAGE

from .models import Post


def pagination(page_number: int,
               post_list: Union[QuerySet, List[Post], Tuple[Post]],
               posts_on_page: int = POSTS_ON_PAGE) -> Page:

    paginator = Paginator(post_list, posts_on_page)
    return paginator.get_page(page_number)
