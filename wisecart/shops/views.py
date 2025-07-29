from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Shop, Review, FeaturedShop
from .forms import ReviewForm

def shop_detail(request, shop_slug):
    # Get the shop object
    shop = get_object_or_404(Shop, slug__iexact=shop_slug)

    # Get all the reviews for the shop
    reviews = shop.reviews.all()

    # Get the number of reviews per page from the request (defaults to 10 if not provided)
    reviews_per_page = request.GET.get('reviews_per_page', 10)  # Default to 10 if not specified

    if reviews_per_page == 'all':
        # If the user selects "all", show all reviews without pagination
        paginated_reviews = reviews
    else:
        try:
            reviews_per_page = int(reviews_per_page)
        except ValueError:
            reviews_per_page = 10  # Default to 10 if invalid input

        # Set up pagination for the reviews
        paginator = Paginator(reviews, reviews_per_page)
        page_number = request.GET.get('page')
        paginated_reviews = paginator.get_page(page_number)

    # Check if the user has already reviewed the shop
    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(shop=shop, user=request.user).first()

    # Initialize form variable
    review_form = None
    
    # Handle form submissions (create, update, or delete reviews)
    if request.method == 'POST':
        if request.user.is_authenticated:
            if 'delete_review' in request.POST:
                if user_review:
                    user_review.delete()
                    return redirect('shops:shop_detail', shop_slug=shop.slug)
            else:
                review_form = ReviewForm(request.POST, instance=user_review)
                if review_form.is_valid():
                    review = review_form.save(commit=False)
                    review.shop = shop
                    review.user = request.user
                    review.save()
                    return redirect('shops:shop_detail', shop_slug=shop.slug)
                # If form is not valid, review_form will contain the POST data and errors
        else:
            return redirect('login')
    
    # Only create form with review data if:
    # 1. Not a POST request, AND
    # 2. User explicitly wants to edit (has 'edit' in GET parameters) OR it's a failed POST
    if review_form is None:  # This means we didn't handle a POST request
        # Check if user wants to edit their existing review
        if user_review and request.GET.get('edit') == 'true':
            review_form = ReviewForm(instance=user_review)
        else:
            # Create a clean form (either for new review or after successful submission)
            review_form = ReviewForm()

    # Pass the necessary data to the template context
    context = {
        'shop': shop,
        'reviews': paginated_reviews,
        'review_form': review_form,
        'user_review': user_review,
        'reviews_per_page': reviews_per_page,
        'show_edit_form': request.GET.get('edit') == 'true',
    }
    return render(request, 'shops/shop_detail.html', context)


def shops(request):
    shops = Shop.objects.all()

    # Get the number of items to display per page from the request
    items_per_page = request.GET.get('items_per_page', 10)  # Default to 10 if not specified

    if items_per_page == 'all':
        # If the user selects "all", we show all shops without pagination
        page_obj = shops
    else:
        try:
            items_per_page = int(items_per_page)
        except ValueError:
            items_per_page = 10  # Default to 10 if invalid input

        # Set up pagination with the selected number of items per page
        paginator = Paginator(shops, items_per_page)

        # Get the current page number from the request
        page_number = request.GET.get('page')

        # Get the page object for the current page
        page_obj = paginator.get_page(page_number)

    # Pass the page_obj and items_per_page to the template context
    context = {
        'page_obj': page_obj,
        'items_per_page': items_per_page,
    }
    return render(request, 'shops/shops.html', context)




def featured_shops(request):
    featured_shops = FeaturedShop.objects.all()
    return render(request, 'shops/featured_shops.html', {'featured_shops': featured_shops})
