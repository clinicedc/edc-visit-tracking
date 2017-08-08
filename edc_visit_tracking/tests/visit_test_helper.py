from model_mommy import mommy

from django.apps import apps as django_apps
from edc_protocol.tests import get_utcnow

from ..constants import SCHEDULED


class VisitTestHelperFutureDate(Exception):
    pass


class VisitTestHelperError(Exception):
    pass


class VisitTestHelper:

    def add_visit(self, model_label=None, visit_code=None, reason=None, subject_identifier=None):
        """Adds (or gets) and returns a visit for give model and code.
        """
        Appointment = django_apps.get_app_config('edc_appointment').model
        reason = reason or SCHEDULED
        model = django_apps.get_model(*model_label.split('.'))
        try:
            appointment = Appointment.objects.get(
                subject_identifier=subject_identifier, visit_code=visit_code)
            if appointment.appt_datetime > get_utcnow():
                raise VisitTestHelperFutureDate(
                    f'For testing, create visits without future dates. '
                    f'Got {appointment.visit_code}, {appointment.appt_datetime}')
            try:
                visit = self.get_visit(
                    visit_code=visit_code,
                    model_label=model_label,
                    subject_identifier=subject_identifier)
            except model.DoesNotExist:
                # create visit for the first time
                visit = mommy.make_recipe(
                    model_label,
                    appointment=appointment,
                    report_datetime=appointment.appt_datetime,
                    reason=reason)
        except Appointment.DoesNotExist as e:
            raise VisitTestHelperError(
                f'{e} {model_label}, {visit_code}. Did you complete the enrollment form?')
        return visit

    def add_visits(self, *codes, model_label=None, subject_identifier=None, reason=None):
        """Adds a sequence of visits for the codes provided.

        If a infant visit already exists, it will just pass.
        """
        visits = []
        for code in codes:
            visits.append(self.add_visit(
                model_label=model_label,
                visit_code=code,
                reason=reason,
                subject_identifier=subject_identifier)
            )
        return visits

    def get_visit(self, visit_code=None, model_label=None, subject_identifier=None):
        """Returns a visit instance if it exists."""
        model = django_apps.get_model(*model_label.split('.'))
        visit = model.objects.get(
            appointment__subject_identifier=subject_identifier, visit_code=visit_code)
        return visit

    def get_last_visit(self, model_label=None, subject_identifier=None):
        """Returns the last visit instance if it exists."""
        model = django_apps.get_model(*model_label.split('.'))
        return model.objects.filter(
            appointment__subject_identifier=subject_identifier).order_by(
                'report_datetime').last()