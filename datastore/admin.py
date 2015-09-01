from django.contrib import admin
from .models import ProjectOwner
from .models import Project
from .models import Block
from .models import ConsumptionMetadata
from .models import ConsumptionRecord
from .models import MeterRun
from .models import DailyUsageBaseline
from .models import DailyUsageReporting
from .models import AnnualUsageBaseline
from .models import AnnualUsageReporting
from .models import GrossSavings
from .models import AnnualSavings
from .models import ModelType
from .models import ModelParameters

admin.site.register(ProjectOwner)
admin.site.register(Project)
admin.site.register(Block)
admin.site.register(ConsumptionMetadata)
admin.site.register(ConsumptionRecord)
admin.site.register(MeterRun)
admin.site.register(DailyUsageBaseline)
admin.site.register(DailyUsageReporting)
admin.site.register(AnnualUsageBaseline)
admin.site.register(AnnualUsageReporting)
admin.site.register(GrossSavings)
admin.site.register(AnnualSavings)
admin.site.register(ModelType)
admin.site.register(ModelParameters)
