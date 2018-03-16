from django.conf.urls import url

from . import views

app_name='reviews'

urlpatterns = [
    # ex: /
    url(r'^$', views.IndexView, name='review_list'),
    # ex: /review/5/
    url(r'^review/(?P<review_id>[0-9]+)/$', views.review_detail, name='review_detail'),
    # ex: /wine/
    url(r'^wine$', views.wine_list, name='wine_list'),
    # ex: /wine/5/
    
    url(r'^wine/(?P<wine_id>[0-9]+)/$', views.wine_detail, name='wine_detail'),
    url(r'^add_review/(?P<wine_id>[0-9]+)/$', views.add_review, name='add_review'),
    # ex: /review/user - get reviews for the logged user
    url(r'^review/user/(?P<username>\w+)/$', views.user_review_list, name='user_review_list'),
    # ex: /review/user - get reviews for the user passed in the url
    url(r'^review/user/$', views.user_review_list, name='user_review_list'),
    # ex: /recommendation - get wine recommendations for the logged user
    url(r'^recommendation/$', views.user_recommendation_list, name='user_recommendation_list'),

    url(r'^home/$', views.review_list, name='home'),

    url(r'^home/register/$',views.user_register,name='register'),

    url(r'^login/$',views.user_login,name='login'),
    url(r'^profile/$',views.user_profile,name='profile'),
    url(r'^logout/$',views.user_logout,name='logout'),    
]