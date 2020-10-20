from edc_adverse_event.constants import DEATH_REPORT_ACTION
from edc_constants.constants import DEAD, HIGH_PRIORITY, YES
from edc_action_item.action_with_notification import ActionWithNotification
from edc_ltfu.constants import LOSS_TO_FOLLOWUP_ACTION

from .constants import VISIT_MISSED_ACTION


class VisitMissedAction(ActionWithNotification):
    name = VISIT_MISSED_ACTION
    display_name = "Submit Loss to Follow Up Report"
    notification_display_name = " Loss to Follow Up Report"
    parent_action_names = []
    show_link_to_changelist = True
    priority = HIGH_PRIORITY

    reference_model = None  # "inte_subject.subjectvisitmissed"
    admin_site_name = None  # "inte_prn_admin"

    def get_next_actions(self):
        next_actions = []
        next_actions = self.append_to_next_if_required(
            next_actions=next_actions,
            action_name=LOSS_TO_FOLLOWUP_ACTION,
            required=self.reference_obj.ltfu == YES,
        )
        next_actions = self.append_to_next_if_required(
            next_actions=next_actions,
            action_name=DEATH_REPORT_ACTION,
            required=self.reference_obj.survival_status == DEAD,
        )
        return next_actions
