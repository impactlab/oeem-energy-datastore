from django.conf.urls import url
from datastore import views

urlpatterns = [
    url(r'^consumption/$', views.ConsumptionMetadataList.as_view()),
    url(r'^consumption/(?P<pk>[0-9]+)/$', views.ConsumptionMetadataDetail.as_view()),
    url(r'^project/$', views.ProjectList.as_view()),
    url(r'^project/(?P<pk>[0-9]+)/$', views.ProjectDetail.as_view()),
    url(r'^project_block/$', views.ProjectBlockList.as_view()),
    url(r'^project_block/(?P<pk>[0-9]+)/$', views.ProjectBlockDetail.as_view()),
    url(r'^meter_run/$', views.MeterRunList.as_view()),
    url(r'^meter_run/(?P<pk>[0-9]+)/$', views.MeterRunDetail.as_view()),
    url(r'^meter_run_summary/(?P<pk>[0-9]+)/$', views.MeterRunSummaryDetail.as_view()),
    url(r'^meter_run_daily/(?P<pk>[0-9]+)/$', views.MeterRunDailyDetail.as_view()),
    url(r'^meter_run_monthly/(?P<pk>[0-9]+)/$', views.MeterRunMonthlyDetail.as_view()),
]
