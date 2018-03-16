from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect,HttpResponse
from django.core.urlresolvers import reverse
from .models import Review, Wine,Cluster
from .forms import ReviewForm
import datetime
from django.contrib.auth.decorators import login_required
from .suggestions import update_clusters
from django.template import RequestContext

from django.shortcuts import render,redirect
from django.shortcuts import render_to_response,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

def IndexView(request):
	return render(request,'reviews/base.html')

def user_profile(request):
    args={'user':request.user}
    return render(request,'reviews/profile.html',args)

def review_list(request):
    latest_review_list = Review.objects.order_by('-pub_date')[:9]
    context = {'latest_review_list':latest_review_list}
    return render(request, 'reviews/review_list.html', context)


def review_detail(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    return render(request, 'reviews/review_detail.html', {'review': review})


def wine_list(request):
    wine_list = Wine.objects.order_by('-name')
    context = {'wine_list':wine_list}
    return render(request, 'reviews/wine_list.html', context)


def wine_detail(request, wine_id):
    wine = get_object_or_404(Wine, pk=wine_id)
    form = ReviewForm()
    return render(request, 'reviews/wine_detail.html', {'wine': wine, 'form': form})


def add_review(request, wine_id):
    wine = get_object_or_404(Wine, pk=wine_id)
    form = ReviewForm(request.POST)
    if form.is_valid():
        rating = form.cleaned_data['rating']
        comment = form.cleaned_data['comment']
        user_name = request.user.username
        review = Review()
        review.wine = wine
        review.user_name = user_name
        review.rating = rating
        review.comment = comment
        review.pub_date = datetime.datetime.now()
        review.save()
        update_clusters()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('reviews:wine_detail', args=(wine.id,)))
    
    return render(request, 'reviews/wine_detail.html', {'wine': wine, 'form': form})


def user_review_list(request, username=None):
    if not username:
        username = request.user.username
    latest_review_list = Review.objects.filter(user_name=username).order_by('-pub_date')
    context = {'latest_review_list':latest_review_list, 'username':username}
    return render(request, 'reviews/user_review_list.html', context)



import sys, os 
import pandas as pd
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "winerama.settings")

import django
django.setup()

from reviews.models import Review, Wine 


def save_review_from_row(review_row):
    review = Review()
    review.id = review_row[0]
    review.user_name = review_row[1]
    review.wine = Wine.objects.get(id=review_row[2])
    review.rating = review_row[3]
    review.pub_date = datetime.datetime.now()
    review.comment = review_row[4]
    review.save()
    
    
# the main function for the script, called by the shell    
if __name__ == "__main__":
    
    # Check number of arguments (including the command name)
    if len(sys.argv) == 2:
        print "Reading from file " + str(sys.argv[1])
        reviews_df = pd.read_csv(sys.argv[1])
        print reviews_df

        # apply save_review_from_row to each review in the data frame
        reviews_df.apply(
            save_review_from_row,
            axis=1
        )

        print "There are {} reviews in DB".format(Review.objects.count())
        
    else:
        print "Please, provide Reviews file path"


@login_required
def user_recommendation_list(request):
    # get this user reviews
    user_reviews = Review.objects.filter(user_name=request.user.username).prefetch_related('wine')
    # from the reviews, get a set of wine IDs
    user_reviews_wine_ids = set(map(lambda x: x.wine.id, user_reviews))
    # then get a wine list excluding the previous IDs
    wine_list = Wine.objects.exclude(id__in=user_reviews_wine_ids)

    return render(
        request, 
        'reviews/user_recommendation_list.html', 
        {'username': request.user.username,'wine_list': wine_list}
    )


from .forms import UserForm

def user_register(request):
    # Like before, get the request's context.
    context = RequestContext(request)

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        
 
        # If the two forms are valid...
        if user_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems

            # Update our variable to tell the template registration was successful.
            registered = True

        else:
            print user_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
    # Render the template depending on the context.
    return render_to_response('reviews/registration_form.html',{'user_form': user_form, 'registered': registered},context)



def user_login(request):
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/reviews/profile/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('reviews/login.html', {}, context)


from django.contrib.auth import logout

#@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    context = RequestContext(request)   
    logout(request)

    # Take the user back to the homepage.
    return render_to_response('reviews/logout.html', {}, context)

