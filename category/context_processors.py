from category.models import Category


def category_menu_links(request):
    links = Category.objects.all()
    return dict(links=links)