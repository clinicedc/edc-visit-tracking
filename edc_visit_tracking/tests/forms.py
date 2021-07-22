from django.forms import ModelForm
from edc_crf.modelform_mixins import CrfModelFormMixin

from edc_visit_tracking.models import SubjectVisitMissed

from ..form_validators import VisitMissedFormValidator


class SubjectVisitMissedForm(CrfModelFormMixin, ModelForm):

    form_validator_cls = VisitMissedFormValidator

    def validate_against_consent(self):
        pass

    class Meta:
        model = SubjectVisitMissed
        fields = "__all__"
