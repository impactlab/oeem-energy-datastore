from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.utils.encoding import python_2_unicode_compatible
from django.db.models.signals import post_save, post_init
from django.dispatch import receiver

from eemeter.evaluation import Period
from eemeter.project import Project as EEMeterProject
from eemeter.consumption import ConsumptionData as EEMeterConsumptionData
from eemeter.location import Location
from eemeter.meter import DataCollection
from eemeter.meter import DefaultResidentialMeter
from eemeter.config.yaml_parser import dump
from eemeter.models.temperature_sensitivity import AverageDailyTemperatureSensitivityModel

from warnings import warn
from datetime import timedelta, datetime
import numpy as np
import json
from collections import defaultdict
import itertools

FUEL_TYPE_CHOICES = [
    ('E', 'electricity'),
    ('NG', 'natural_gas'),
]

ENERGY_UNIT_CHOICES = [
    ('KWH', 'kWh'),
    ('THM', 'therm'),
]

PROJECT_ATTRIBUTE_DATA_TYPE_CHOICES = [
    ('BOOLEAN', 'boolean_value'),
    ('CHAR', 'char_value'),
    ('DATE', 'date_value'),
    ('DATETIME', 'datetime_value'),
    ('FLOAT', 'float_value'),
    ('INTEGER', 'integer_value'),
]

def _json_clean(value):
    if value is None or np.isnan(value) or np.isinf(value):
        return None
    else:
        return value


@python_2_unicode_compatible
class ProjectOwner(models.Model):
    user = models.OneToOneField(User)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return u'ProjectOwner {}'.format(self.user.username)

class ProjectManager(models.Manager):

    def recent_meter_runs(self, project_pks=[]):
        from django.db import connection
        cursor = connection.cursor()

        meter_runs = ''' 
          SELECT DISTINCT ON (meter.consumption_metadata_id)
            meter.*
          FROM datastore_meterrun AS meter
          JOIN datastore_project AS project
            ON meter.project_id = project.id
        '''
        
        qargs = []

        if project_pks:
            meter_runs = ''' 
              {}
              WHERE project.id IN %s
            '''.format(meter_runs)
            qargs.append(tuple(project_pks))

        meter_runs = ''' 
          {}
          ORDER BY meter.consumption_metadata_id,
            meter.added DESC
        '''.format(meter_runs)
        
        cursor.execute(meter_runs, qargs)
        
        columns = [col[0] for col in cursor.description]
        
        results = []
        for row in cursor.fetchall():
            results.append(MeterRun(**dict(zip(columns, row))))

        return results

    def attributes(self):
        return self.projectattribute_set

@python_2_unicode_compatible
class Project(models.Model):
    project_owner = models.ForeignKey(ProjectOwner)
    project_id = models.CharField(max_length=255, null=False, unique=True)
    baseline_period_start = models.DateTimeField(blank=True, null=True)
    baseline_period_end = models.DateTimeField(blank=True, null=True)
    reporting_period_start = models.DateTimeField(blank=True, null=True)
    reporting_period_end = models.DateTimeField(blank=True, null=True)
    zipcode = models.CharField(max_length=10, blank=True, null=True)
    weather_station = models.CharField(max_length=10, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    #objects = models.Manager()
    objects = ProjectManager()

    def __str__(self):
        return u'Project {}'.format(self.project_id)

    @property
    def baseline_period(self):
        return Period(self.baseline_period_start, self.baseline_period_end)

    @property
    def reporting_period(self):
        return Period(self.reporting_period_start, self.reporting_period_end)

    @property
    def lat_lng(self):
        if self.latitude is not None and self.longitude is not None:
            return (self.latitude, self.longitude)
        else:
            return None

    def eemeter_project(self):
        if self.lat_lng is not None:
            location = Location(lat_lng=self.lat_lng)
        elif self.weather_station is not None:
            location = Location(station=self.weather_station)
        else:
            location = Location(zipcode=self.zipcode)
        consumption = [cm.eemeter_consumption_data() for cm in self.consumptionmetadata_set.all()]
        consumption_metadata_ids = [cm.id for cm in self.consumptionmetadata_set.all()]

        project = EEMeterProject(location, consumption, self.baseline_period, self.reporting_period)
        return project, consumption_metadata_ids

    def run_meter(self, meter_type='residential', start_date=None, end_date=None, n_days=None):
        """ If possible, run the meter specified by meter_type.
        """
        try:
            project, cm_ids = self.eemeter_project()
        except ValueError:
            message = "Cannot create eemeter project; skipping project id={}.".format(self.project_id)
            warn(message)
            return

        if meter_type == "residential":
            meter = DefaultResidentialMeter()
        elif meter_type == "commercial":
            raise NotImplementedError
        else:
            raise NotImplementedError

        if start_date is None:
            start_date = now()
            for consumption_data in project.consumption:
                try:
                    earliest_date = consumption_data.data.index[0].to_datetime()
                    if earliest_date < start_date:
                        start_date = earliest_date
                except IndexError:
                    pass

        if end_date is None:
            end_date = now()

        daily_evaluation_period = Period(start_date, end_date)

        meter_results = meter.evaluate(DataCollection(project=project))

        meter_runs = []
        for consumption_data, cm_id in zip(project.consumption, cm_ids):

            fuel_type_tag = consumption_data.fuel_type

            # determine model type
            if fuel_type_tag == "electricity":
                meter_type_suffix = "E"
                model = AverageDailyTemperatureSensitivityModel(heating=True,cooling=True)
            elif fuel_type_tag == "natural_gas":
                meter_type_suffix = "NG"
                model = AverageDailyTemperatureSensitivityModel(heating=True,cooling=False)
            else:
                raise NotImplementedError

            if meter_type == "residential":
                meter_type_str = "DFLT_RES_" + meter_type_suffix
            elif model_type == "commercial":
                meter_type_str = "DFLT_COM_" + meter_type_suffix

            # gather meter results
            annual_usage_baseline = meter_results.get_data("annualized_usage", ["baseline", fuel_type_tag])
            if annual_usage_baseline is not None:
                annual_usage_baseline = annual_usage_baseline.value

            annual_usage_reporting = meter_results.get_data("annualized_usage", ["reporting", fuel_type_tag])
            if annual_usage_reporting is not None:
                annual_usage_reporting = annual_usage_reporting.value

            gross_savings = meter_results.get_data("gross_savings", [fuel_type_tag])
            if gross_savings is not None:
                gross_savings = gross_savings.value

            annual_savings = None
            if annual_usage_baseline is not None and annual_usage_reporting is not None:
                annual_savings = annual_usage_baseline - annual_usage_reporting

            # gather meter results
            cvrmse_baseline = meter_results.get_data("cvrmse", ["baseline", fuel_type_tag])
            if cvrmse_baseline is not None:
                cvrmse_baseline = cvrmse_baseline.value

            cvrmse_reporting = meter_results.get_data("cvrmse", ["reporting", fuel_type_tag])
            if cvrmse_reporting is not None:
                cvrmse_reporting = cvrmse_reporting.value

            model_parameter_json_baseline = meter_results.get_data("model_params", ["baseline", fuel_type_tag])
            model_parameter_array_baseline = None
            if model_parameter_json_baseline is not None:
                model_parameter_dict_baseline = model_parameter_json_baseline.value.to_dict()
                model_parameter_json_baseline = json.dumps(model_parameter_dict_baseline)
                model_parameters_baseline = model.param_type(model_parameter_dict_baseline)

            model_parameter_json_reporting = meter_results.get_data("model_params", ["reporting", fuel_type_tag])
            model_parameter_array_reporting = None
            if model_parameter_json_reporting is not None:
                model_parameter_dict_reporting = model_parameter_json_reporting.value.to_dict()
                model_parameter_json_reporting = json.dumps(model_parameter_dict_reporting)
                model_parameters_reporting = model.param_type(model_parameter_dict_reporting)

            meter_run = MeterRun(project=self,
                    consumption_metadata=ConsumptionMetadata.objects.get(pk=cm_id),
                    serialization=dump(meter.meter),
                    annual_usage_baseline=annual_usage_baseline,
                    annual_usage_reporting=annual_usage_reporting,
                    gross_savings=gross_savings,
                    annual_savings=annual_savings,
                    meter_type=meter_type_str,
                    model_parameter_json_baseline=model_parameter_json_baseline,
                    model_parameter_json_reporting=model_parameter_json_reporting,
                    cvrmse_baseline=cvrmse_baseline,
                    cvrmse_reporting=cvrmse_reporting)

            meter_run.save()
            meter_runs.append(meter_run)

            # record time series of usage for baseline and reporting
            avg_temps = project.weather_source.daily_temperatures(
                    daily_evaluation_period, meter.temperature_unit_str)

            values_baseline = model.transform(avg_temps, model_parameters_baseline)
            values_reporting = model.transform(avg_temps, model_parameters_reporting)

            month_names = [daily_evaluation_period.start.strftime("%Y-%m")]

            month_groups_baseline = defaultdict(list)
            month_groups_reporting = defaultdict(list)

            for value_baseline, value_reporting, days in zip(values_baseline, values_reporting, range(daily_evaluation_period.timedelta.days)):
                date = daily_evaluation_period.start + timedelta(days=days)

                daily_usage_baseline = DailyUsageBaseline(meter_run=meter_run, value=value_baseline, date=date)
                daily_usage_baseline.save()

                daily_usage_reporting = DailyUsageReporting(meter_run=meter_run, value=value_reporting, date=date)
                daily_usage_reporting.save()

                # track monthly usage as well
                current_month = date.strftime("%Y-%m")
                if not current_month == month_names[-1]:
                    month_names.append(current_month)

                month_groups_baseline[current_month].append(value_baseline)
                month_groups_reporting[current_month].append(value_reporting)

            for month_name in month_names:
                baseline_values = month_groups_baseline[month_name]
                reporting_values = month_groups_reporting[month_name]

                monthly_average_baseline = 0 if baseline_values == [] else np.nanmean(baseline_values)
                monthly_average_reporting = 0 if reporting_values == [] else np.nanmean(reporting_values)

                dt = datetime.strptime(month_name, "%Y-%m")
                monthly_average_usage_baseline = MonthlyAverageUsageBaseline(meter_run=meter_run, value=monthly_average_baseline, date=dt)
                monthly_average_usage_baseline.save()

                monthly_average_usage_reporting = MonthlyAverageUsageReporting(meter_run=meter_run, value=monthly_average_reporting, date=dt)
                monthly_average_usage_reporting.save()

        return meter_runs
    
    @staticmethod
    def recent_meter_runs(project_pks=[]):

        from django.db import connection
        cursor = connection.cursor()

        meter_runs = ''' 
          SELECT DISTINCT ON (consumption.id)
            project.id,
            consumption.id,
            meter.*,
            consumption.fuel_type
          FROM datastore_meterrun AS meter
          JOIN datastore_consumptionmetadata AS consumption
            ON meter.consumption_metadata_id = consumption.id
          JOIN datastore_project AS project
            ON meter.project_id = project.id
        '''
        
        qargs = []

        if project_pks:
            meter_runs = ''' 
              {}
              WHERE project.id IN %s
            '''.format(meter_runs)
            qargs.append(tuple(project_pks))

        meter_runs = ''' 
          {}
          ORDER BY consumption.id,
            meter.added DESC
        '''.format(meter_runs)
        
        cursor.execute(meter_runs, qargs)
        
        meterrun_columns = [col[0] for col in cursor.description[2:-1]]
        
        results = {}
        for consumption_id, rows in itertools.groupby(cursor.fetchall(), key=lambda x: x[1]):
            
            grouped_rows = list(rows)
            results[grouped_rows[0][0]] = [{
                'meterrun': MeterRun(**dict(zip(meterrun_columns, row[2:-1]))),
                'fuel_type': row[-1]
            } for row in grouped_rows]

        return results
    # def recent_meter_runs(self):
    #     consumption_metadatas = self.consumptionmetadata_set.all()
    #     meter_runs = []
    #     for cm in consumption_metadatas:
    #         try:
    #             meter_runs.append(cm.meterrun_set.latest('added'))
    #         except MeterRun.DoesNotExist:
    #             pass
    #     return meter_runs

    # def attributes(self):
    #     return self.projectattribute_set.all()



@python_2_unicode_compatible
class ProjectAttributeKey(models.Model):
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100)
    data_type = models.CharField(max_length=25, choices=PROJECT_ATTRIBUTE_DATA_TYPE_CHOICES)

    def __str__(self):
        return u'"{}" ({}, {})'.format(self.display_name, self.name, self.data_type)


@python_2_unicode_compatible
class ProjectAttribute(models.Model):
    project = models.ForeignKey(Project)
    key = models.ForeignKey(ProjectAttributeKey)
    boolean_value = models.NullBooleanField(blank=True, null=True)
    char_value = models.CharField(max_length=100, blank=True, null=True)
    date_value = models.DateField(blank=True, null=True)
    datetime_value = models.DateTimeField(blank=True, null=True)
    float_value = models.FloatField(blank=True, null=True)
    integer_value = models.IntegerField(blank=True, null=True)

    def value(self):
        if self.key.data_type == "BOOLEAN":
            return self.boolean_value
        elif self.key.data_type == "CHAR":
            return self.char_value
        elif self.key.data_type == "DATE":
            return self.date_value
        elif self.key.data_type == "DATETIME":
            return self.datetime_value
        elif self.key.data_type == "FLOAT":
            return self.float_value
        elif self.key.data_type == "INTEGER":
            return self.integer_value
        else:
            return None

    def __str__(self):
        return u'({}, {}, project:{})'.format(self.key.name, self.value(), self.project)


@python_2_unicode_compatible
class ProjectBlock(models.Model):
    name = models.CharField(max_length=255)
    projects = models.ManyToManyField(Project)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return u'(name={}, n_projects={})'.format(self.name, self.projects.count())

    def run_meters(self, meter_type='residential', start_date=None, end_date=None, n_days=None):
        """ Run meter for each project in the project block.
        """
        for project in self.projects.all():
            project.run_meter(meter_type, start_date, end_date, n_days)

    def compute_summary_timeseries(self):
        """ Compute aggregate timeseries for all projects in project block.
        """
        data_by_fuel_type = defaultdict(lambda: {
            "baseline_by_month": defaultdict(list),
            "baseline_by_date": defaultdict(list),
            "actual_by_month": defaultdict(list),
            "actual_by_date": defaultdict(list),
            "reporting_by_month": defaultdict(list),
            "reporting_by_date": defaultdict(list),
            "n_completed_projects_by_date": defaultdict(lambda: 0),
        })

        for project in self.projects.all():
            for meter_run in project.recent_meter_runs():

                fuel_type = meter_run.consumption_metadata.fuel_type
                dailyusagebaseline_set = meter_run.dailyusagebaseline_set.all()
                dailyusagereporting_set = meter_run.dailyusagereporting_set.all()
                assert len(dailyusagebaseline_set) == len(dailyusagereporting_set)

                fuel_type_data = data_by_fuel_type[fuel_type]
                baseline_by_month = fuel_type_data["baseline_by_month"]
                baseline_by_date = fuel_type_data["baseline_by_date"]
                actual_by_month = fuel_type_data["actual_by_month"]
                actual_by_date = fuel_type_data["actual_by_date"]
                reporting_by_month = fuel_type_data["reporting_by_month"]
                reporting_by_date = fuel_type_data["reporting_by_date"]
                n_completed_projects_by_date = fuel_type_data["n_completed_projects_by_date"]

                for daily_usage_baseline, daily_usage_reporting in \
                        zip(dailyusagebaseline_set, dailyusagereporting_set):

                    # should be the same as the month for the reporting period
                    date = daily_usage_baseline.date
                    month = date.strftime("%Y-%m")

                    baseline_value = daily_usage_baseline.value
                    reporting_value = daily_usage_reporting.value

                    if date > project.reporting_period_start.date():
                        actual_value = reporting_value
                        n_completed_projects_by_date[date] += 1
                    else:
                        actual_value = baseline_value

                    baseline_by_month[month].append(baseline_value)
                    baseline_by_date[date].append(baseline_value)
                    actual_by_month[month].append(actual_value)
                    actual_by_date[date].append(actual_value)
                    reporting_by_month[month].append(reporting_value)
                    reporting_by_date[date].append(reporting_value)

        for fuel_type, fuel_type_data in data_by_fuel_type.items():

            baseline_by_month = fuel_type_data["baseline_by_month"]
            baseline_by_date = fuel_type_data["baseline_by_date"]
            actual_by_month = fuel_type_data["actual_by_month"]
            actual_by_date = fuel_type_data["actual_by_date"]
            reporting_by_month = fuel_type_data["reporting_by_month"]
            reporting_by_date = fuel_type_data["reporting_by_date"]
            n_completed_projects_by_date = fuel_type_data["n_completed_projects_by_date"]

            date_labels = sorted(baseline_by_date.keys())
            month_labels = sorted(baseline_by_month.keys())

            fuel_type_summary = FuelTypeSummary(project_block=self,
                    fuel_type=fuel_type)
            fuel_type_summary.save()

            for date in date_labels:
                DailyUsageSummaryBaseline(fuel_type_summary=fuel_type_summary,
                        value=np.nansum(baseline_by_date[date]), date=date).save()
                DailyUsageSummaryActual(fuel_type_summary=fuel_type_summary,
                        value=np.nansum(actual_by_date[date]), date=date,
                        n_projects=n_completed_projects_by_date[date]).save()
                DailyUsageSummaryReporting(fuel_type_summary=fuel_type_summary,
                        value=np.nansum(reporting_by_date[date]), date=date).save()

            for month in month_labels:
                date = datetime.strptime(month, "%Y-%m").date()
                MonthlyUsageSummaryBaseline(fuel_type_summary=fuel_type_summary,
                        value=np.nansum(baseline_by_month[month]), date=date).save()
                MonthlyUsageSummaryActual(fuel_type_summary=fuel_type_summary,
                        value=np.nansum(actual_by_month[month]), date=date,
                        n_projects=n_completed_projects_by_date[date]).save()
                MonthlyUsageSummaryReporting(fuel_type_summary=fuel_type_summary,
                        value=np.nansum(reporting_by_month[month]), date=date).save()

    def recent_summaries(self):
        fuel_types = set([fts['fuel_type'] for fts in self.fueltypesummary_set.values('fuel_type')])
        return [self.fueltypesummary_set.filter(fuel_type=fuel_type).latest('added') for fuel_type in fuel_types]


@python_2_unicode_compatible
class ConsumptionMetadata(models.Model):
    fuel_type = models.CharField(max_length=3, choices=FUEL_TYPE_CHOICES)
    energy_unit = models.CharField(max_length=3, choices=ENERGY_UNIT_CHOICES)
    project = models.ForeignKey(Project, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def eemeter_consumption_data(self):
        records = self.records.all()
        records = [r.eemeter_record() for r in records]
        fuel_type = dict(FUEL_TYPE_CHOICES)[self.fuel_type]
        unit_name = dict(ENERGY_UNIT_CHOICES)[self.energy_unit]
        consumption_data = EEMeterConsumptionData(records, fuel_type=fuel_type,
                unit_name=unit_name, record_type="arbitrary_start")
        return consumption_data

    def __str__(self):
        n = len(self.records.all())
        return u'ConsumptionMetadata(fuel_type={}, energy_unit={}, n={})'.format(self.fuel_type, self.energy_unit, n)


@python_2_unicode_compatible
class ConsumptionRecord(models.Model):
    metadata = models.ForeignKey(ConsumptionMetadata, related_name="records")
    start = models.DateTimeField()
    value = models.FloatField(blank=True, null=True)
    estimated = models.BooleanField()

    def __str__(self):
        return u'Consumption(start={}, value={}, estimated={})'.format(self.start, self.value, self.estimated)

    class Meta:
        ordering = ['start']

    def eemeter_record(self):
        return {"start": self.start, "value": self.value, "estimated": self.estimated }


@python_2_unicode_compatible
class MeterRun(models.Model):
    METER_TYPE_CHOICES = (
        ('DFLT_RES_E', 'Default Residential Electricity'),
        ('DFLT_RES_NG', 'Default Residential Natural Gas'),
        ('DFLT_COM_E', 'Default Commercial Electricity'),
        ('DFLT_COM_NG', 'Default Commercial Natural Gas'),
    )
    project = models.ForeignKey(Project)
    consumption_metadata = models.ForeignKey(ConsumptionMetadata)
    serialization = models.CharField(max_length=100000, blank=True, null=True)
    annual_usage_baseline = models.FloatField(blank=True, null=True)
    annual_usage_reporting = models.FloatField(blank=True, null=True)
    gross_savings = models.FloatField(blank=True, null=True)
    annual_savings = models.FloatField(blank=True, null=True)
    meter_type = models.CharField(max_length=250, choices=METER_TYPE_CHOICES, blank=True, null=True)
    model_parameter_json_baseline = models.CharField(max_length=10000, blank=True, null=True)
    model_parameter_json_reporting = models.CharField(max_length=10000, blank=True, null=True)
    cvrmse_baseline = models.FloatField(blank=True, null=True)
    cvrmse_reporting = models.FloatField(blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return u'MeterRun(project_id={}, valid={})'.format(self.project.project_id, self.valid_meter_run())

    def annual_usage_baseline_clean(self):
        return _json_clean(self.annual_usage_baseline)

    def annual_usage_reporting_clean(self):
        return _json_clean(self.annual_usage_reporting)

    def gross_savings_clean(self):
        return _json_clean(self.gross_savings)

    def annual_savings_clean(self):
        return _json_clean(self.annual_savings)

    def cvrmse_baseline_clean(self):
        return _json_clean(self.cvrmse_baseline)

    def cvrmse_reporting_clean(self):
        return _json_clean(self.cvrmse_reporting)

    @property
    def fuel_type(self):
        return self.consumption_metadata.fuel_type

    def valid_meter_run(self, threshold=20):
        if self.cvrmse_baseline is None or self.cvrmse_reporting is None:
            return False
        return self.cvrmse_baseline < threshold and self.cvrmse_reporting < threshold


@python_2_unicode_compatible
class DailyUsageBaseline(models.Model):
    meter_run = models.ForeignKey(MeterRun)
    value = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return u'DailyUsageBaseline(date={}, value={})'.format(self.date, self.value)

    class Meta:
        ordering = ['date']

    def value_clean(self):
        return _json_clean(self.value)


@python_2_unicode_compatible
class DailyUsageReporting(models.Model):
    meter_run = models.ForeignKey(MeterRun)
    value = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return u'DailyUsageReporting(date={}, value={})'.format(self.date, self.value)

    class Meta:
        ordering = ['date']

    def value_clean(self):
        return _json_clean(self.value)


@python_2_unicode_compatible
class MonthlyAverageUsageBaseline(models.Model):
    meter_run = models.ForeignKey(MeterRun)
    value = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return u'MonthlyAverageUsageBaseline(date={}, value={})'.format(self.date, self.value)

    class Meta:
        ordering = ['date']

    def value_clean(self):
        return _json_clean(self.value)


@python_2_unicode_compatible
class MonthlyAverageUsageReporting(models.Model):
    meter_run = models.ForeignKey(MeterRun)
    value = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return u'MonthlyAverageUsageReporting(date={}, value={})'.format(self.date, self.value)

    class Meta:
        ordering = ['date']

    def value_clean(self):
        return _json_clean(self.value)


@python_2_unicode_compatible
class FuelTypeSummary(models.Model):
    project_block = models.ForeignKey(ProjectBlock)
    fuel_type = models.CharField(max_length=3, choices=FUEL_TYPE_CHOICES)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return u'FuelTypeSummary(project_block={}, fuel_type={})'.format(self.project_block, self.fuel_type)


@python_2_unicode_compatible
class DailyUsageSummaryBaseline(models.Model):
    fuel_type_summary = models.ForeignKey(FuelTypeSummary)
    value = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return u'DailyUsageSummaryBaseline(date={}, value={})'.format(self.date, self.value)

    class Meta:
        ordering = ['date']


@python_2_unicode_compatible
class DailyUsageSummaryActual(models.Model):
    fuel_type_summary = models.ForeignKey(FuelTypeSummary)
    value = models.FloatField()
    date = models.DateField()
    n_projects = models.IntegerField()

    def __str__(self):
        return u'DailyUsageSummaryActual(date={}, value={})'.format(self.date, self.value)

    class Meta:
        ordering = ['date']


@python_2_unicode_compatible
class DailyUsageSummaryReporting(models.Model):
    fuel_type_summary = models.ForeignKey(FuelTypeSummary)
    value = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return u'DailyUsageSummaryReporting(date={}, value={})'.format(self.date, self.value)

    class Meta:
        ordering = ['date']


@python_2_unicode_compatible
class MonthlyUsageSummaryBaseline(models.Model):
    fuel_type_summary = models.ForeignKey(FuelTypeSummary)
    value = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return u'MonthlyUsageSummaryBaseline(date={}, value={})'.format(self.date, self.value)

    class Meta:
        ordering = ['date']


@python_2_unicode_compatible
class MonthlyUsageSummaryActual(models.Model):
    fuel_type_summary = models.ForeignKey(FuelTypeSummary)
    value = models.FloatField()
    date = models.DateField()
    n_projects = models.IntegerField()

    def __str__(self):
        return u'MonthlyUsageSummaryActual(date={}, value={})'.format(self.date, self.value)

    class Meta:
        ordering = ['date']


@python_2_unicode_compatible
class MonthlyUsageSummaryReporting(models.Model):
    fuel_type_summary = models.ForeignKey(FuelTypeSummary)
    value = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return u'MonthlyUsageSummaryReporting(date={}, value={})'.format(self.date, self.value)

    class Meta:
        ordering = ['date']


# # if project set changed, recompute the summary timeseries.
# TODO if needed, uncomment when this can be moved into the background, otherwise too slow.
# @receiver(post_init, sender=ProjectBlock)
# def project_block_compute_summary_timeseries(sender, instance, **kwargs):
#     instance.__projects = instance.projects
#
# @receiver(post_save, sender=ProjectBlock)
# def project_block_compute_summary_timeseries(sender, instance, **kwargs):
#     if instance.__projects != instance.projects:
#         instance.compute_summary_timeseries()
#         instance.__projects = instance.projects

@receiver(post_save, sender=User)
def create_project_owner(sender, instance, **kwargs):
    project_owner, created = ProjectOwner.objects.get_or_create(user=instance)
