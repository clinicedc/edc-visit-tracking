from typing import Any, Optional

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from edc_appointment.appointment_status_updater import AppointmentStatusUpdater
from edc_appointment.choices import APPT_TIMING
from edc_appointment.constants import MISSED_APPT, SCHEDULED_APPT, UNSCHEDULED_APPT
from edc_constants.constants import INCOMPLETE
from edc_metadata.metadata_helper_mixin import MetaDataHelperMixin
from edc_visit_schedule.utils import is_baseline

from .constants import MISSED_VISIT, SCHEDULED, UNSCHEDULED
from .utils import get_subject_visit_missed_model_cls


class SubjectVisitReasonUpdaterError(Exception):
    pass


class SubjectVisitReasonUpdaterBaselineError(Exception):
    pass


class SubjectVisitReasonUpdaterCrfsExistsError(Exception):
    pass


class SubjectVisitReasonUpdaterRequisitionsExistsError(Exception):
    pass


class SubjectVisitReasonUpdaterMissedVisitNotAllowed(Exception):
    pass


class SubjectVisitReasonUpdater(MetaDataHelperMixin):
    """A class to try to update `reason` field based on the
    response from appointment timing and appointment reason.
    """

    instance_attr = "appointment"

    def __init__(
        self,
        appointment: Optional[Any] = None,
        appt_timing: Optional[str] = None,
        appt_reason: Optional[str] = None,
    ):
        self.appointment = appointment
        if not getattr(self.appointment, "id", None):
            raise SubjectVisitReasonUpdaterError(
                "Appointment instance must exist. Got `id` is None"
            )
        self.appt_timing = appt_timing or self.appointment.appt_timing
        if self.appt_timing not in [a for a, b in APPT_TIMING]:
            raise SubjectVisitReasonUpdaterError(
                f"Invalid value for appt_timing. "
                f"Expected on of {[a for a, b in APPT_TIMING]}. Got {self.appt_timing}"
            )
        self.appt_reason = appt_reason or self.appointment.appt_reason
        try:
            self.subject_visit = getattr(
                self.appointment, self.appointment.related_visit_model_attr()
            )
        except ObjectDoesNotExist:
            self.subject_visit = None
        except AttributeError as e:
            if "related_visit_model_attr" not in str(e):
                raise
            self.subject_visit = None

    def update_or_raise(self) -> None:
        if self.appt_timing == MISSED_APPT and is_baseline(instance=self.appointment):
            raise SubjectVisitReasonUpdaterBaselineError(
                "Invalid. A baseline appointment may not be reported `missed`"
            )
        elif self.appt_timing == MISSED_APPT and self.appt_reason in [
            SCHEDULED_APPT,
            UNSCHEDULED_APPT,
        ]:
            self._update_visit_to_missed_or_raise()
        elif self.appt_timing != MISSED_APPT and self.appt_reason in [
            SCHEDULED_APPT,
            UNSCHEDULED_APPT,
        ]:
            self._update_visit_to_not_missed_or_raise()
        else:
            raise SubjectVisitReasonUpdaterError(
                f"Condition not handled. Got appt_reason={self.appt_reason}, "
                f"appt_timing={self.appt_timing}"
            )

    def _update_visit_to_missed_or_raise(self):
        self.missed_visit_allowed_or_raise()
        if self.subject_visit:
            AppointmentStatusUpdater(self.appointment)
            self.subject_visit.reason = MISSED_VISIT
            self.subject_visit.document_status = INCOMPLETE
            self.subject_visit.save_base(update_fields=["reason", "document_status"])
            self.subject_visit.refresh_from_db()

    def _update_visit_to_not_missed_or_raise(self):
        """Updates the subject visit instance from MISSED_VISIT
        to SCHEDULED or UNSCHEDULED.
        """
        if self.subject_visit:
            AppointmentStatusUpdater(self.appointment)
            reason = self.get_reason_from_appt_reason(self.appt_reason)
            self.delete_subject_visit_missed_if_exists()
            self.subject_visit.reason = reason
            self.subject_visit.document_status = INCOMPLETE
            if self.subject_visit.comments:
                self.subject_visit.comments = self.subject_visit.comments.replace(
                    "[auto-created]", ""
                )
            self.subject_visit.save_base(
                update_fields=["reason", "document_status", "comments"]
            )
            self.subject_visit.refresh_from_db()

    def missed_visit_allowed_or_raise(self) -> None:
        """Raises an exception if not allowed.

        May be not allowed by settings attr or
        if CRF/Requisition metadata already exists.

        See also: EDC_VISIT_TRACKING_ALLOW_MISSED_UNSCHEDULED
        """
        if (
            self.appointment.visit_code_sequence > 0
            and not self.allow_missed_unscheduled_appts
        ):
            raise SubjectVisitReasonUpdaterMissedVisitNotAllowed(
                "Invalid. An unscheduled appointment may not be reported `missed`."
                "Try to cancel the appointment instead. "
            )
        else:
            self.raise_if_keyed_data_exists()

    def raise_if_keyed_data_exists(self) -> None:
        """Raises an exception if CRF or Requisition metadata exists"""
        if self.crf_metadata_keyed_exists:
            raise SubjectVisitReasonUpdaterCrfsExistsError(
                "Invalid. CRFs have already been entered for this timepoint."
            )
        elif self.requisition_metadata_keyed_exists:
            raise SubjectVisitReasonUpdaterRequisitionsExistsError(
                "Invalid. Requisitions have already been entered " "for this timepoint."
            )

    def delete_subject_visit_missed_if_exists(self) -> None:
        """Deletes the subject visit missed report if it exists"""
        get_subject_visit_missed_model_cls().objects.filter(
            subject_visit__appointment=self.appointment
        ).delete()

    def get_reason_from_appt_reason(self, appt_reason: str) -> str:
        """Returns a subject visit reason given the appt reason"""
        if appt_reason == SCHEDULED_APPT:
            visit_reason = SCHEDULED
        elif appt_reason == UNSCHEDULED_APPT and self.appointment.visit_code_sequence > 0:
            visit_reason = UNSCHEDULED
        else:
            raise SubjectVisitReasonUpdaterError(
                "Update failed. This is not an unscheduled appointment. "
                f"Got visit_code_sequence > 0 for appt_reason={appt_reason}"
            )
        return visit_reason

    @property
    def allow_missed_unscheduled_appts(self) -> bool:
        """Returns value of settings attr or False"""
        return getattr(settings, "EDC_VISIT_TRACKING_ALLOW_MISSED_UNSCHEDULED", False)