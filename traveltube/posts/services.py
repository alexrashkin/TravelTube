from django.core.paginator import Paginator


def make_pages(request, post_list, NUMBER_POSTS):
    paginator = Paginator(post_list, NUMBER_POSTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
