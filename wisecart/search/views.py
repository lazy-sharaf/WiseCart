from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Min
from .models import SearchResult, Search
from scraper.scraper.spiders.ryans import RyansSpider
from scraper.scraper.spiders.startech import StartechSpider
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from crochet import setup, wait_for
import logging

logger = logging.getLogger(__name__)
setup()


def search(request):
    if request.method == "POST":
        search_term = request.POST.get("search_term", "")
        if search_term:
            # Create a Search object when form is submitted
            Search.objects.create(
                query=search_term,
                user=request.user if request.user.is_authenticated else None,
            )
            return redirect(f"/results/?q={search_term}")

    # Update trending searches query to work with new model
    week_ago = timezone.now() - timedelta(days=7)
    trending_searches = (
        SearchResult.objects.filter(search__time__gte=week_ago)
        .values("search__query")
        .annotate(search_count=Count("search__query"), min_price=Min("price"))
        .order_by("-search_count")[:8]
    )

    return render(
        request, "search/index.html", {"trending_searches": trending_searches}
    )


def results(request):
    search_term = request.GET.get("q", "")
    if not search_term:
        return redirect("/")

    try:
        # Create or get the search object
        search_obj, created = Search.objects.get_or_create(
            query=search_term,
            user=request.user if request.user.is_authenticated else None,
            defaults={"time": timezone.now()},
        )

        # If not created, update the time
        if not created:
            search_obj.time = timezone.now()
            search_obj.save()

        # Check for recent results
        recent_results = SearchResult.objects.filter(
            search=search_obj, search__time__gte=timezone.now() - timedelta(hours=24)
        )

        if recent_results.exists():
            logger.info(
                f"Found {recent_results.count()} recent results for '{search_term}'"
            )
            store_count = recent_results.values("store__name").distinct().count()
            return render(
                request,
                "search/results.html",
                {
                    "results": recent_results.order_by("price"),
                    "search_term": search_term,
                    "store_count": store_count,
                },
            )

        # If no recent results, run the spiders
        logger.info(f"No recent results found for '{search_term}', starting spiders")

        @wait_for(timeout=30)
        def run_spiders():
            settings = get_project_settings()
            settings.set(
                "ITEM_PIPELINES",
                {"scraper.scraper.pipelines.SearchResultPipeline": 300},
            )

            runner = CrawlerRunner(settings)

            # Delete old results for this search
            SearchResult.objects.filter(search=search_obj).delete()

            # Run both spiders
            deferred = runner.crawl(
                StartechSpider, search_term=search_term, search_obj=search_obj
            )
            deferred.addCallback(
                lambda _: runner.crawl(
                    RyansSpider, search_term=search_term, search_obj=search_obj
                )
            )
            return deferred

        # Run spiders and wait for results
        run_spiders()

        # Get the new results
        results = SearchResult.objects.filter(search=search_obj).order_by("price")
        store_count = results.values("store__name").distinct().count()

        logger.info(
            f"Spiders completed, found {results.count()} results for '{search_term}'"
        )

        return render(
            request,
            "search/results.html",
            {
                "results": results,
                "search_term": search_term,
                "store_count": store_count,
            },
        )

    except Exception as e:
        logger.error(f"Error in search results view: {str(e)}")
        return render(
            request,
            "search/results.html",
            {
                "error": "An error occurred while fetching results.",
                "search_term": search_term,
                "store_count": 0,
            },
        )
