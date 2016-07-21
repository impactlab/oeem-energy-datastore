from django.conf.urls import url
from api_doc.views import (
    MySwaggerResourcesView,
    MySwaggerUIView
)

from rest_framework_swagger.views import SwaggerApiView


urlpatterns = [
    url(r'^$', MySwaggerUIView.as_view(), name="django.swagger.base.view"),
    url(r'^api-docs/$', MySwaggerResourcesView.as_view(),
        name="django.swagger.resources.view"),
    url(r'^api-docs/(?P<path>.*)/?$', SwaggerApiView.as_view(),
        name='django.swagger.api.view'),
]
