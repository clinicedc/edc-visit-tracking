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

.. |pypi| image:: https://img.shields.io/pypi/v/edc-visit-tracking.svg
    :target: https://pypi.python.org/pypi/edc-visit-tracking
    
.. |travis| image:: https://travis-ci.com/clinicedc/edc-visit-tracking.svg?branch=develop
    :target: https://travis-ci.com/clinicedc/edc-visit-tracking
    
.. |codecov| image:: https://codecov.io/gh/clinicedc/edc-visit-tracking/branch/develop/graph/badge.svg
  :target: https://codecov.io/gh/clinicedc/edc-visit-tracking

.. |downloads| image:: https://pepy.tech/badge/edc-visit-tracking
   :target: https://pepy.tech/project/edc-visit-tracking
