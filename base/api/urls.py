from django.conf.urls import url
from base.api import views
from rest_framework.authtoken.views import ObtainAuthToken

urlpatterns = [
    url(r'^category/$', views.CategoryView.as_view()),
    url(r'^product/$', views.ProductView.as_view()),
    url(r'^login/$', ObtainAuthToken.as_view()),

]