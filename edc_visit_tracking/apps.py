import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style

style = color_style()

ATTR = 0
MODEL_LABEL = 1


class AppConfig(DjangoAppConfig):
    name = "edc_visit_tracking"
    verbose_name = "Edc Visit Tracking"

    # report_datetime_allowance:
    #   set to not allow CRF report_datetimes to exceed the
    #   visit report_datetime
    #   by more than X days. Set to -1 to ignore
    report_datetime_allowance = 30
    allow_crf_report_datetime_before_visit = False
    reason_field = {}

    def ready(self):
        from .signals import visit_tracking_check_in_progress_on_post_save

        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
