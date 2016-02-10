from django.contrib import admin
from . import models

admin.site.register(models.ProjectOwner)
admin.site.register(models.Project)
admin.site.register(models.ProjectBlock)
admin.site.register(models.ProjectAttributeKey)
admin.site.register(models.ProjectAttribute)
admin.site.register(models.ConsumptionMetadata)
admin.site.register(models.ConsumptionRecord)
admin.site.register(models.MeterRun)
admin.site.register(models.DailyUsageBaseline)
admin.site.register(models.DailyUsageReporting)
admin.site.register(models.MonthlyAverageUsageBaseline)
admin.site.register(models.MonthlyAverageUsageReporting)
admin.site.register(models.MonthlyUsageSummaryBaseline)
admin.site.register(models.MonthlyUsageSummaryActual)
admin.site.register(models.MonthlyUsageSummaryReporting)
admin.site.register(models.DailyUsageSummaryBaseline)
admin.site.register(models.DailyUsageSummaryActual)
admin.site.register(models.DailyUsageSummaryReporting)
admin.site.register(models.FuelTypeSummary)

admin.site.site_header = "Open Energy Efficiency Meter"
