from django import forms
from .models import Machine, Maintenance, Claim, Directory, User

class MachineForm(forms.ModelForm):
    class Meta:
        model = Machine
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['model'].queryset = Directory.objects.filter(entity_name="Модель техники")
        self.fields['engine_model'].queryset = Directory.objects.filter(entity_name="Модель двигателя")
        self.fields['transmission_model'].queryset = Directory.objects.filter(entity_name="Модель трансмиссии")
        self.fields['drive_axle_model'].queryset = Directory.objects.filter(entity_name="Модель ведущего моста")
        self.fields['steer_axle_model'].queryset = Directory.objects.filter(entity_name="Модель управляемого моста")
        self.fields['client_user'].queryset = User.objects.filter(role='client')
        self.fields['service_user'].queryset = User.objects.filter(role='service')

class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = '__all__'
        widgets = {
            'machine': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['maintenance_type'].queryset = Directory.objects.filter(entity_name="Вид ТО")
        self.fields['service_company'].queryset = Directory.objects.filter(entity_name="Сервисная компания")
        self._force_service_company = None

        if user and user.role == 'service':
            org_name = user.get_full_name() or user.username
            directory_obj = Directory.objects.filter(entity_name="Сервисная компания", name=org_name).first()
            if directory_obj:
                self.fields['service_company'].initial = directory_obj
                self.fields['service_company'].disabled = True
                self._force_service_company = directory_obj
        elif user and user.role == 'client':
            directory_obj = Directory.objects.filter(entity_name="Сервисная компания", name="самостоятельно").first()
            if directory_obj:
                self.fields['service_company'].initial = directory_obj
                self.fields['service_company'].disabled = True
                self._force_service_company = directory_obj

    def clean_service_company(self):

        if self._force_service_company:
            return self._force_service_company
        return self.cleaned_data['service_company']

class ClaimForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['failed_unit'].queryset = Directory.objects.filter(entity_name="Узел отказа")
        self.fields['recovery_method'].queryset = Directory.objects.filter(entity_name="Способ восстановления")
        self.fields['service_company'].queryset = Directory.objects.filter(entity_name="Сервисная компания")

        # 1. Если сервисная организация — автоподставить по пользователю
        if user and user.role == 'service':
            org_name = user.get_full_name() or user.username
            directory_obj = Directory.objects.filter(entity_name="Сервисная компания", name=org_name).first()
            if directory_obj:
                self.fields['service_company'].initial = directory_obj
                self.fields['service_company'].disabled = True

        # 2. Если клиент — автоподставить по машине (если есть)
        elif user and user.role == 'client':
            machine = None

            if 'machine' in self.initial and self.initial['machine']:
                machine = self.initial['machine']

            elif 'machine' in self.data and self.data['machine']:
                try:
                    machine = Machine.objects.get(pk=self.data['machine'])
                except Machine.DoesNotExist:
                    machine = None

            elif getattr(self.instance, 'machine', None):
                machine = self.instance.machine

            if machine and getattr(machine, 'service_user', None):
                org_name = machine.service_user.get_full_name() or machine.service_user.username
                directory_obj = Directory.objects.filter(entity_name="Сервисная компания", name=org_name).first()
                if directory_obj:
                    self.fields['service_company'].initial = directory_obj
                    self.fields['service_company'].disabled = True
