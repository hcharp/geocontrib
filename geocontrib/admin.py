import logging
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.contrib.gis import admin
from django.urls import path
from django.utils.translation import ugettext_lazy as _
from django.template.response import TemplateResponse

from geocontrib.models import Authorization
from geocontrib.models import Feature
from geocontrib.models import Project
from geocontrib.models import Subscription
from geocontrib.models import FeatureType
from geocontrib.models import Layer
from geocontrib.models import CustomField
from geocontrib.models import UserLevelPermission
# from geocontrib.models import CustomFieldInterface

logger = logging.getLogger(__name__)
User = get_user_model()


class FeatureTypeForm(forms.ModelForm):
    class Meta:
        model = FeatureType
        fields = '__all__'
        widgets = {
            'color': forms.widgets.TextInput(attrs={'type': 'color'}),
        }


class CustomFieldModelForm(forms.ModelForm):
    alias = forms.CharField(
        label="Alias",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Indiquez un alias pour cette colonne"
        })
    )

    class Meta:
        model = CustomField
        fields = ('label', 'alias')

    def save(self, *args, **kwargs):
        return None


class HiddenDeleteBaseFormSet(forms.BaseFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.fields[forms.formsets.DELETION_FIELD_NAME].widget = forms.HiddenInput()


class HiddenDeleteModelFormSet(forms.BaseModelFormSet, HiddenDeleteBaseFormSet):
    pass


class FeatureSelectFieldForm(forms.Form):
    related_field = forms.ChoiceField(
        label="Champs à ajouter",
        choices=[(str(field.name), str(field.name)) for field in Feature._meta.get_fields()],
        required=False
    )
    alias = forms.CharField(
        label="Alias",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Indiquez un alias pour cette colonne"
        })
    )


class SearchConditionForm(forms.Form):

    logical_operator = forms.ChoiceField(
        label="Opérateur logique",
        choices=[(option, option) for option in ('', 'AND', 'OR', 'XOR')],
        required=False
    )
    related_field = forms.ChoiceField(
        label="Champs à ajouter",
        choices=[(str(field.name), str(field.name)) for field in Feature._meta.get_fields()],
        required=False
    )
    comparison_operator = forms.ChoiceField(
        label="Opérateur de comparaison",
        choices=[(option, option) for option in ('=', '!=', '<', '<=', '>', '>=')],
        required=False
    )
    value = forms.CharField(label="Valeur", required=False)


class UserAdmin(DjangoUserAdmin):

    list_display = (
        'email', 'last_name', 'first_name',
        'is_superuser', 'is_administrator', 'is_staff', 'is_active'
    )
    search_fields = ('id', 'email', 'first_name', 'last_name')

    ordering = ('-pk', )
    verbose_name_plural = 'utilisateurs'
    verbose_name = 'utilisateur'

    readonly_fields = (
        'id',
        'date_joined',
        'last_login',
    )

    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password')
        }),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name',)
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'is_administrator',
                'groups', 'user_permissions'),
        }),
        (_('Important dates'), {
            'fields': (
                'last_login', 'date_joined'),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2', 'first_name', 'last_name',
                'is_active', 'is_staff', 'is_superuser'),
        }),
    )


class CustomFieldTabular(admin.TabularInline):
    model = CustomField
    extra = 0
    can_delete = False
    can_order = True
    show_change_link = True
    view_on_site = False


class FeatureTypeAdmin(admin.ModelAdmin):
    form = FeatureTypeForm
    readonly_fields = ('geom_type', )
    inlines = (
        CustomFieldTabular,
    )

    change_form_template = 'admin/geocontrib/with_create_postrgres_view.html'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                '<int:feature_type_id>/create-postgres-view/',
                self.admin_site.admin_view(self.create_postgres_view),
                name='create_postgres_view'),
        ]
        return my_urls + urls

    def create_postgres_view(self, request, feature_type_id, *args, **kwargs):
        from django.forms import formset_factory
        from django.forms import modelformset_factory
        from django.shortcuts import redirect
        from django.contrib import messages

        FeatureDetailSelectionFormset = formset_factory(
            FeatureSelectFieldForm,
            formset=HiddenDeleteBaseFormSet,
            can_delete=True,
            extra=2
        )

        SearchConditionFormset = formset_factory(
            SearchConditionForm,
            formset=HiddenDeleteBaseFormSet,
            can_delete=True,
            extra=1
        )

        CustomFieldsFormSet = modelformset_factory(
            CustomField,
            can_delete=True,
            form=CustomFieldModelForm,
            formset=HiddenDeleteModelFormSet,
            extra=0,
        )

        if request.method == 'POST':
            fds_formset = FeatureDetailSelectionFormset(request.POST or None, prefix='fds')
            sc_formset = SearchConditionFormset(request.POST or None, prefix='sc')
            cfs_formset = CustomFieldsFormSet(request.POST or None, prefix='cfs')
            if fds_formset.is_valid() and sc_formset.is_valid() and cfs_formset.is_valid():

                # handle feature field selection
                for data in fds_formset.cleaned_data:
                    print(data)
                # handle feature field selection
                for data in sc_formset.cleaned_data:
                    print(data)
                # handle feature field selection
                for data in cfs_formset.cleaned_data:
                    print(data)

                messages.success(request, 'La vue est diponible. ')
                return redirect('admin:geocontrib_featuretype_change', feature_type_id)
            else:
                for formset in [fds_formset, sc_formset, cfs_formset]:
                    logger.error(formset.errors)

        else:
            fds_formset = FeatureDetailSelectionFormset(prefix='fds')
            sc_formset = SearchConditionFormset(prefix='sc')
            cfs_formset = CustomFieldsFormSet(
                queryset=CustomField.objects.filter(feature_type__pk=feature_type_id), prefix='cfs')

        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['cfs_formset'] = cfs_formset
        context['fds_formset'] = fds_formset
        context['sc_formset'] = sc_formset

        return TemplateResponse(request, "admin/geocontrib/create_postrges_view_form.html", context)


class FlatPageAdmin(FlatPageAdmin):
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'sites')}),
        (_('Advanced options'), {
            'classes': ('collapse',),
            'fields': (
                'enable_comments',
                'registration_required',
                'template_name',
            ),
        }),
    )


admin.site.register(User, UserAdmin)
admin.site.register(CustomField)
admin.site.register(Layer)
admin.site.register(Authorization)
admin.site.register(Feature)
admin.site.register(FeatureType, FeatureTypeAdmin)
admin.site.register(Project)
admin.site.register(Subscription)
admin.site.register(UserLevelPermission)
# admin.site.register(CustomFieldInterface)
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)
