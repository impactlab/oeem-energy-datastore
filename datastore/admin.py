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
