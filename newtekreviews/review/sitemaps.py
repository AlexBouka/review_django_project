from django.contrib.sitemaps import Sitemap

from .models import Review


class ReviewSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.9

    def items(self):
        return Review.published.all()

    def lastmod(self, obj):
        return obj.time_updated
