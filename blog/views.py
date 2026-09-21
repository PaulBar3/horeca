from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import Article


def blog_list(request):
    news_articles = Article.objects.filter(is_published=True, category="news")

    return render(request, "blog/blog_list.html", {
        "news_articles": news_articles[:6],
    })


def article_list(request):
    articles = Article.objects.filter(is_published=True)

    category = request.GET.get("category", "recipe")
    if category:
        articles = articles.filter(category=category)

    paginator = Paginator(articles, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "blog/article_list.html", {
        "articles": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "page_obj": page_obj,
    })


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    return render(request, "blog/article_detail.html", {"article": article})
