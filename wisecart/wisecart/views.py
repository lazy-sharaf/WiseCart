from django.shortcuts import render
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from search.models import Search
from shops.models import Shop


def index(request):
    # Calculate the date 7 days ago
    one_week_ago = timezone.now() - timedelta(days=7)

    # Get the most searched terms within the last week
    most_searched_terms = (
        Search.objects.filter(time__gte=one_week_ago)
        .values("query")
        .annotate(search_count=Count("query"))
        .order_by("-search_count")[:9]
    )

    shops = Shop.objects.all()[:4]

    return render(
        request,
        "index.html",
        {
            "most_searched_terms": most_searched_terms,
            "shops": shops,
        },
    )


def about(request):
    return render(request, "about.html")


def privacy_policy(request):
    return render(request, "privacy_policy.html")


def help_center(request):
    return render(request, "help_center.html")


def terms_of_service(request):
    return render(request, "terms_of_service.html")


def contact_us(request):
    return render(request, "contact_us.html")

