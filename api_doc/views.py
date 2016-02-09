from rest_framework_swagger.views import SwaggerUIView
from rest_framework_swagger.views import SwaggerApiView
from rest_framework_swagger.views import SwaggerResourcesView
import rest_framework_swagger as rfs

from django.conf import settings
from django.shortcuts import render_to_response, RequestContext
from django.utils.safestring import mark_safe

import json


def get_full_base_path(request):
    try:
        base_path = rfs.SWAGGER_SETTINGS['base_path']
    except KeyError:
        return request.build_absolute_uri(request.path).rstrip('/')

    try:
        protocol = rfs.SWAGGER_SETTINGS['protocol']
    except KeyError:
        protocol = 'https' if self.request.is_secure() else 'http'

    return '{0}://{1}'.format(protocol, base_path.rstrip('/'))

class MySwaggerUIView(SwaggerUIView):

    def get(self, request, *args, **kwargs):

        if not self.has_permission(request):
            return self.handle_permission_denied(request)

        template_name = rfs.SWAGGER_SETTINGS.get('template_path')
        data = {
            'swagger_settings': {
                'discovery_url': "%s/api-docs/" % get_full_base_path(request),
                'api_key': rfs.SWAGGER_SETTINGS.get('api_key', ''),
                'api_version': rfs.SWAGGER_SETTINGS.get('api_version', ''),
                'token_type': rfs.SWAGGER_SETTINGS.get('token_type'),
                'enabled_methods': mark_safe(
                    json.dumps(rfs.SWAGGER_SETTINGS.get('enabled_methods'))),
                'doc_expansion': rfs.SWAGGER_SETTINGS.get('doc_expansion', ''),
            },
            'rest_framework_settings': {
                'DEFAULT_VERSIONING_CLASS':
                    settings.REST_FRAMEWORK.get('DEFAULT_VERSIONING_CLASS', '')
                    if hasattr(settings, 'REST_FRAMEWORK') else None,

            },
            'django_settings': {
                'CSRF_COOKIE_NAME': mark_safe(
                    json.dumps(getattr(settings, 'CSRF_COOKIE_NAME', 'csrftoken'))),
            }
        }
        response = render_to_response(
            template_name, RequestContext(request, data))

        return response

class MySwaggerResourcesView(SwaggerUIView):

    def get_base_path(self):
        try:
            base_path = rfs.SWAGGER_SETTINGS['base_path']
        except KeyError:
            return self.request.build_absolute_uri(
                self.request.path).rstrip('/')
        try:
            protocol = rfs.SWAGGER_SETTINGS['protocol']
        except KeyError:
            protocol = 'https' if self.request.is_secure() else 'http'

        return '{0}://{1}/{2}'.format(protocol, base_path, 'api-docs')
