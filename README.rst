|pypi| |travis| |codecov| |downloads|

edc-visit-tracking
------------------

Track study participant visit reports.


Declaring a visit model
+++++++++++++++++++++++

A **visit_model** is declared using the model mixin `VisitModelMixin`. Normally, a **visit_model** will be declared with additional model mixins, but `VisitModelMixin` must be there.


.. code-block:: python

    class SubjectVisit(VisitModelMixin, BaseUuidModel):
        ...

Also, ensure the `Meta` class attributes of `VisitModelMixin` are inherited. These include required constraints and ordering.


.. code-block:: python

    class SubjectVisit(VisitModelMixin, BaseUuidModel):
    
        ...
        
        class Meta(VisitModelMixin.Meta):
            pass
    
Among other features, `VisitModelMixin` adds a `OneToOneField` foreign key to the **visit_model** that points to `edc_appointment.Appointment`.

 Important: A **visit model** is a special model in the EDC. A model declared with the model mixin, `VisitModelMixin`, is the definition of a **visit model**. CRFs and Requisitions have a foreign key pointing to a **visit model**. A number of methods on CRFs and Requisitions detect their **visit model** foreign key name, model class and value by looking for the FK declared with `VisitModelMixin`.


For a subject that requires ICF the **visit model** would look like this:

.. code-block:: python

    class SubjectVisit(VisitModelMixin, OffstudyMixin, CreatesMetadataModelMixin,
                       RequiresConsentModelMixin, BaseUuidModel):
    
        class Meta(VisitModelMixin.Meta):
            consent_model = 'myapp.subjectconsent'  # for RequiresConsentModelMixin
            

If the subject does not require ICF, such as an infant, don't include the `RequiresConsentModelMixin`:

.. code-block:: python

    class InfantVisit(VisitModelMixin, OffstudyMixin,
                      CreatesMetadataModelMixin, BaseUuidModel):
    
        class Meta(VisitModelMixin.Meta):
            pass

Declaring a CRF
+++++++++++++++

The `CrfModelMixin` is required for all CRF models. CRF models have a `OneToOneField` key to a **visit model**.

.. code-block:: python

    class CrfOne(CrfModelMixin, OffstudyCrfModelMixin, RequiresConsentModelMixin,
                 UpdatesCrfMetadataModelMixin, BaseUuidModel):
    
        subject_visit = models.OneToOneField(SubjectVisit)
    
        f1 = models.CharField(max_length=10, default='erik')
    
        vl = models.CharField(max_length=10, default=NO)
    
        rdb = models.CharField(max_length=10, default=NO)
    
        class Meta:
            consent_model = 'myapp.subjectconsent'  # for RequiresConsentModelMixin

Declaring forms:
++++++++++++++++
The `VisitFormMixin` includes a number of common validations in the `clean` method:

.. code-block:: python

    class SubjectVisitForm(VisitFormMixin, forms.ModelForm):
    
        class Meta:
            model = SubjectVisit

`PreviousVisitModelMixin`
+++++++++++++++++++++++++

The `PreviousVisitModelMixin` ensures that visits are entered in sequence. It is included with the `VisitModelMixin`.

`VisitTrackingModelFormMixin`
+++++++++++++++++++++++++++++

    see `DEFAULT_REPORT_DATETIME_ALLOWANCE`


Missed Visit Report
+++++++++++++++++++

A detail report should be submitted for scheduled visits that are missed.
By selecting the reason ``missed visit`` on ``SubjectVisit``, only the missed visit CRF will be required
for the timepoint. All other CRFs and requisitions will be excluded.

Unscheduled visits cannot be missed.

The model mixin ``SubjectVisitMissedModelMixin`` provides the basic features of a `SubjectVisitMissed` model.

In your subject app declare:

.. code-block:: python

    from django.db.models import PROTECT
    from edc_crf.model_mixins import CrfWithActionModelMixin
    from edc_model import models as edc_models
    from edc_visit_tracking.model_mixins import SubjectVisitMissedModelMixin

    class SubjectVisitMissed(SubjectVisitMissedModelMixin, edc_models.BaseUuidModel):

        missed_reasons = models.ManyToManyField(
            SubjectVisitMissedReasons, blank=True, related_name="+"
        )

        class Meta(CrfWithActionModelMixin.Meta, edc_models.BaseUuidModel.Meta):
            verbose_name = "Missed Visit Report"
            verbose_name_plural = "Missed Visit Report"

In your list model app, e.g. ``meta_lists``, declare the list model:

.. code-block:: python

    class SubjectVisitMissedReasons(ListModelMixin):
        class Meta(ListModelMixin.Meta):
            verbose_name = "Subject Missed Visit Reasons"
            verbose_name_plural = "Subject Missed Visit Reasons"

... and update the ``list_data`` dictionary, for example:

.. code-block:: python

    list_data = {
    ...
    "meta_lists.subjectvisitmissedreasons": [
        ("forgot", "Forgot / Can’t remember being told about appointment"),
        ("family_emergency", "Family emergency (e.g. funeral) and was away"),
        ("travelling", "Away travelling/visiting"),
        ("working_schooling", "Away working/schooling"),
        ("too_sick", "Too sick or weak to come to the centre"),
        ("lack_of_transport", "Transportation difficulty"),
        (OTHER, "Other reason (specify below)",),
    ],
    ...
    }


.. |pypi| image:: https://img.shields.io/pypi/v/edc-visit-tracking.svg
    :target: https://pypi.python.org/pypi/edc-visit-tracking
    
.. |travis| image:: https://travis-ci.com/clinicedc/edc-visit-tracking.svg?branch=develop
    :target: https://travis-ci.com/clinicedc/edc-visit-tracking
    
.. |codecov| image:: https://codecov.io/gh/clinicedc/edc-visit-tracking/branch/develop/graph/badge.svg
  :target: https://codecov.io/gh/clinicedc/edc-visit-tracking

.. |downloads| image:: https://pepy.tech/badge/edc-visit-tracking
   :target: https://pepy.tech/project/edc-visit-tracking
