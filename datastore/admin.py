from django.contrib import admin
from . import models

admin.site.register(models.ProjectOwner)
admin.site.register(models.Project)
admin.site.register(models.ProjectBlock)
admin.site.register(models.ProjectAttributeKey)
admin.site.register(models.ProjectAttribute)
admin.site.register(models.ConsumptionMetadata)
admin.site.register(models.ConsumptionRecord)
# admin.site.register(models.MeterRun)
admin.site.register(models.ProjectRun)

admin.site.site_header = "Open Energy Efficiency Meter"
