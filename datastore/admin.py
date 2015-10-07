from django.contrib import admin
from .models import ProjectOwner
from .models import Project
from .models import ProjectBlock
from .models import ConsumptionMetadata
from .models import ConsumptionRecord
from .models import MeterRun
from .models import DailyUsageBaseline
from .models import DailyUsageReporting
from .models import MonthlyAverageUsageBaseline
from .models import MonthlyAverageUsageReporting
from .models import MonthlyUsageSummaryBaseline
from .models import MonthlyUsageSummaryActual
from .models import MonthlyUsageSummaryReporting
from .models import DailyUsageSummaryBaseline
from .models import DailyUsageSummaryActual
from .models import DailyUsageSummaryReporting
from .models import FuelTypeSummary

admin.site.register(ProjectOwner)
admin.site.register(Project)
admin.site.register(ProjectBlock)
admin.site.register(ConsumptionMetadata)
admin.site.register(ConsumptionRecord)
admin.site.register(MeterRun)
admin.site.register(DailyUsageBaseline)
admin.site.register(DailyUsageReporting)
admin.site.register(MonthlyAverageUsageBaseline)
admin.site.register(MonthlyAverageUsageReporting)
admin.site.register(MonthlyUsageSummaryBaseline)
admin.site.register(MonthlyUsageSummaryActual)
admin.site.register(MonthlyUsageSummaryReporting)
admin.site.register(DailyUsageSummaryBaseline)
admin.site.register(DailyUsageSummaryActual)
admin.site.register(DailyUsageSummaryReporting)
admin.site.register(FuelTypeSummary)

admin.site.site_header = "Open Energy Efficiency Meter"
