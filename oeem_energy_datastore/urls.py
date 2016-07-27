import os

from django.views.generic.base import RedirectView
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings

from rest_framework.routers import DefaultRouter

from datastore import views as datastore_views
from portal import views as portal_views
from registry import views as registry_views
from letsencrypt import views as letsencrypt_views

router = DefaultRouter()

router.register(
    r'projects',
    datastore_views.ProjectViewSet,
    base_name='project')

router.register(
    r'project_runs',
    datastore_views.ProjectRunViewSet,
    base_name='project_run')

router.register(
    r'project_attribute_keys',
    datastore_views.ProjectAttributeKeyViewSet,
    base_name='project_attribute_key')

router.register(
    r'project_attributes',
    datastore_views.ProjectAttributeViewSet,
    base_name='project_attribute')

router.register(
    r'project_owners',
    datastore_views.ProjectOwnerViewSet,
    base_name='project_owner')

router.register(
    r'project_blocks',
    datastore_views.ProjectBlockViewSet,
    base_name='project_block')

router.register(
    r'consumption_metadatas',
    datastore_views.ConsumptionMetadataViewSet,
    base_name='consumption_metadata')

router.register(
    r'consumption_records',
    datastore_views.ConsumptionRecordViewSet,
    base_name='consumption_record')

router.register(
    r'project_results',
    datastore_views.ProjectResultViewSet,
    base_name='project_result')

challenge_slug = os.environ.get("CHALLENGE_SLUG")

urlpatterns = [
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^oauth2/', include('oauth2_provider.urls',
        namespace='oauth2_provider')),
    url(r'^docs/', include('api_doc.urls')),
    url(r'^api/v1/', include(router.urls)),
    url(r'^portal/$', portal_views.index, name='index'),
    url(r'^portal/project_results/$', portal_views.meter_runs,
        name='project_results_table'),
    url(r'^portal/csv_export/$', portal_views.csv_export,
        name='portal_csv_export'),
    url(r'^registry/summary/$', registry_views.RegistrySummary.as_view(),
        name='registry_summary'),
    url(r'^\.well-known/acme-challenge/%s$' % challenge_slug,
        letsencrypt_views.challenge, name='letsencrypt_challenge'),
    url(r'^$', RedirectView.as_view(url='admin/', permanent=False),
        name='index')
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns.append(url(r'^__debug__/', include(debug_toolbar.urls)))
