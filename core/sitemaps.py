from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from blog.models import Article
from catalog.models import Product


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "weekly"

    def items(self):
        return [
            "core:home",
            "core:about",
            "core:b2b",
            "core:contacts",
            "catalog:product_list",
            "blog:article_list",
        ]

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Product.objects.all()

    def lastmod(self, obj):
        return obj.updated_at


class ArticleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Article.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at
