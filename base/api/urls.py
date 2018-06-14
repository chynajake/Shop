from django.conf.urls import url
from base.api import views

urlpatterns = [
    url(r'^category/$', views.CategoryView.as_view()),
]