[![Build Status](https://travis-ci.org/clinicedc/edc-visit-tracking.svg?branch=develop)](https://travis-ci.org/clinicedc/edc-visit-tracking) [![Coverage Status](https://coveralls.io/repos/clinicedc/edc-visit-tracking/badge.svg?branch=develop&service=github)](https://coveralls.io/github/clinicedc/edc-visit-tracking?branch=develop)

# edc-visit-tracking

Track study participant visit reports.


### Declaring a visit model

A __visit_model__ is declared using the model mixin `VisitModelMixin`. Normally, a __visit_model__ will be declared with additional model mixins, but `VisitModelMixin` must be there.

    class SubjectVisit(VisitModelMixin, BaseUuidModel):
        ...

Also, ensure the `Meta` class attributes of `VisitModelMixin` are inherited. These include required constraints and ordering.

    class SubjectVisit(VisitModelMixin, BaseUuidModel):
    
        ...
        
        class Meta(VisitModelMixin.Meta):
            pass
    
Among other features, `VisitModelMixin` adds a `OneToOneField` foreign key to the __visit_model__ that points to `edc_appointment.Appointment`.

> Important: A __visit model__ is a special model in the EDC. A model declared with the model mixin, `VisitModelMixin`, is the definition of a __visit model__. CRFs and Requisitions have a foreign key pointing to a __visit model__. A number of methods on CRFs and Requisitions detect their __visit model__ foreign key name, model class and value by looking for the FK declared with `VisitModelMixin`.


For a subject that requires ICF the __visit model__ would look like this:

    class SubjectVisit(VisitModelMixin, OffstudyMixin, CreatesMetadataModelMixin, RequiresConsentModelMixin, BaseUuidModel):
    
        class Meta(VisitModelMixin.Meta):
            consent_model = 'myapp.subjectconsent'  # for RequiresConsentModelMixin
            

If the subject does not require ICF, such as an infant, don't include the `RequiresConsentModelMixin`:

    class InfantVisit(VisitModelMixin, OffstudyMixin, CreatesMetadataModelMixin, BaseUuidModel):
    
        class Meta(VisitModelMixin.Meta):
            pass

### Declaring a CRF

The `CrfModelMixin` is required for all CRF models. CRF models have a `OneToOneField` key to a __visit model__.

    class CrfOne(CrfModelMixin, OffstudyCrfModelMixin, RequiresConsentModelMixin, UpdatesCrfMetadataModelMixin, BaseUuidModel):
    
        subject_visit = models.OneToOneField(SubjectVisit)
    
        f1 = models.CharField(max_length=10, default='erik')
    
        vl = models.CharField(max_length=10, default=NO)
    
        rdb = models.CharField(max_length=10, default=NO)
    
        class Meta:
            consent_model = 'myapp.subjectconsent'  # for RequiresConsentModelMixin

### Declaring forms:

The `VisitFormMixin` includes a number of common validations in the `clean` method:

    class SubjectVisitForm(VisitFormMixin, forms.ModelForm):
    
        class Meta:
            model = SubjectVisit

### `PreviousVisitModelMixin`

The `PreviousVisitModelMixin` ensures that visits are entered in sequence. It is included with the `VisitModelMixin`.
