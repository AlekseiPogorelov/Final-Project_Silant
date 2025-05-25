from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Machine, Maintenance, Claim, Directory
from .forms import MachineForm, MaintenanceForm, ClaimForm
from import_export import resources, fields, widgets
from import_export.admin import ImportExportModelAdmin


# --- Фирменные заголовки админки ---
admin.site.site_header = "Мой Силант — Администрирование"
admin.site.site_title = "Мой Силант"
admin.site.index_title = "Управление данными"

# --- Пользователь с ролями ---
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )
    list_display = BaseUserAdmin.list_display + ('role',)
    list_filter = BaseUserAdmin.list_filter + ('role',)

admin.site.register(User, UserAdmin)

# --- Импорт/экспорт для Directory ---
class DirectoryResource(resources.ModelResource):
    class Meta:
        model = Directory

@admin.register(Directory)
class DirectoryAdmin(ImportExportModelAdmin):
    resource_class = DirectoryResource
    list_display = ('entity_name', 'name', 'description')
    search_fields = ('entity_name', 'name', 'description')
    list_filter = ('entity_name',)

# --- Импорт/экспорт для Machine ---
class MachineResource(resources.ModelResource):
    serial_number = fields.Field(
        attribute='serial_number',
        column_name='Зав. № машины'
    )
    model = fields.Field(
        attribute='model',
        column_name='Модель техники',
        widget=widgets.ForeignKeyWidget(Directory, 'name')
    )
    engine_model = fields.Field(
        attribute='engine_model',
        column_name='Модель двигателя',
        widget=widgets.ForeignKeyWidget(Directory, 'name')
    )
    engine_serial = fields.Field(
        attribute='engine_serial',
        column_name='Зав. № двигателя'
    )
    transmission_model = fields.Field(
        attribute='transmission_model',
        column_name='Модель трансмиссии (производитель, артикул)',
        widget=widgets.ForeignKeyWidget(Directory, 'name')
    )
    transmission_serial = fields.Field(
        attribute='transmission_serial',
        column_name='Зав. № трансмиссии'
    )
    drive_axle_model = fields.Field(
        attribute='drive_axle_model',
        column_name='Модель ведущего моста',
        widget=widgets.ForeignKeyWidget(Directory, 'name')
    )
    drive_axle_serial = fields.Field(
        attribute='drive_axle_serial',
        column_name='Зав. № ведущего моста'
    )
    steer_axle_model = fields.Field(
        attribute='steer_axle_model',
        column_name='Модель управляемого моста',
        widget=widgets.ForeignKeyWidget(Directory, 'name')
    )
    steer_axle_serial = fields.Field(
        attribute='steer_axle_serial',
        column_name='Зав. № управляемого моста'
    )
    shipment_date = fields.Field(
        attribute='shipment_date',
        column_name='Дата отгрузки с завода'
    )
    client = fields.Field(
        attribute='client',
        column_name='Покупатель'
    )
    consignee = fields.Field(
        attribute='consignee',
        column_name='Грузополучатель (конечный потребитель)'
    )
    delivery_address = fields.Field(
        attribute='delivery_address',
        column_name='Адрес поставки (эксплуатации)'
    )
    equipment = fields.Field(
        attribute='equipment',
        column_name='Комплектация (доп. опции)'
    )
    service_company = fields.Field(
        attribute='service_company',
        column_name='Сервисная компания'
    )
    class Meta:
        model = Machine
        import_id_fields = ['serial_number']

@admin.register(Machine)
class MachineAdmin(ImportExportModelAdmin):
    form = MachineForm
    resource_class = MachineResource
    list_display = (
        'serial_number', 'model', 'engine_model', 'transmission_model',
        'drive_axle_model', 'steer_axle_model', 'shipment_date',
        'client_user', 'service_user', 'service_company'
    )
    search_fields = ('serial_number', 'service_company')
    list_filter = (
        'model', 'engine_model', 'transmission_model',
        'drive_axle_model', 'steer_axle_model', 'client_user', 'service_user', 'service_company'
    )
    autocomplete_fields = [
        'model', 'engine_model', 'transmission_model',
        'drive_axle_model', 'steer_axle_model', 'client_user', 'service_user'
    ]
    fieldsets = (
        (None, {
            'fields': (
                'serial_number', 'model', 'engine_model', 'engine_serial',
                'transmission_model', 'transmission_serial',
                'drive_axle_model', 'drive_axle_serial',
                'steer_axle_model', 'steer_axle_serial',
                'contract', 'shipment_date', 'client', 'client_user',
                'consignee', 'delivery_address', 'equipment', 'service_user', 'service_company'
            )
        }),
    )

# --- Импорт/экспорт для Maintenance ---
class MaintenanceResource(resources.ModelResource):
    machine = fields.Field(
        attribute='machine',
        column_name='Зав. № машины',
        widget=widgets.ForeignKeyWidget(Machine, 'serial_number')
    )
    maintenance_type = fields.Field(
        attribute='maintenance_type',
        column_name='Вид ТО',
        widget=widgets.ForeignKeyWidget(Directory, 'name')
    )
    date = fields.Field(
        attribute='date',
        column_name='Дата проведения ТО'
    )
    operating_time = fields.Field(
        attribute='operating_time',
        column_name='Наработка, м/час'
    )
    order_number = fields.Field(
        attribute='order_number',
        column_name='№ заказ-наряда'
    )
    order_date = fields.Field(
        attribute='order_date',
        column_name='дата заказ-наряда'
    )
    service_company = fields.Field(
        attribute='service_company',
        column_name='Организация, проводившая ТО',
        widget=widgets.ForeignKeyWidget(Directory, 'name')
    )
    class Meta:
        model = Maintenance
        import_id_fields = ['machine', 'maintenance_type', 'date']

@admin.register(Maintenance)
class MaintenanceAdmin(ImportExportModelAdmin):
    form = MaintenanceForm
    resource_class = MaintenanceResource
    list_display = (
        'machine', 'maintenance_type', 'date', 'operating_time',
        'order_number', 'order_date', 'service_company'
    )
    search_fields = ('machine__serial_number',)
    list_filter = ('maintenance_type', 'service_company', 'date')
    autocomplete_fields = ['machine', 'maintenance_type', 'service_company']
    fieldsets = (
        (None, {
            'fields': (
                'machine', 'maintenance_type', 'date', 'operating_time',
                'order_number', 'order_date', 'service_company'
            )
        }),
    )

# --- Импорт/экспорт для Claim ---
class ClaimResource(resources.ModelResource):
    machine = fields.Field(
        attribute='machine',
        column_name='Зав. № машины',
        widget=widgets.ForeignKeyWidget(Machine, 'serial_number')
    )
    failure_date = fields.Field(
        attribute='failure_date',
        column_name='Дата отказа'
    )
    operating_time = fields.Field(
        attribute='operating_time',
        column_name='Наработка, м/час'
    )
    failed_unit = fields.Field(
        attribute='failed_unit',
        column_name='Узел отказа',
        widget=widgets.ForeignKeyWidget(Directory, 'name')
    )
    failure_description = fields.Field(
        attribute='failure_description',
        column_name='Описание отказа'
    )
    recovery_method = fields.Field(
        attribute='recovery_method',
        column_name='Способ восстановления',
        widget=widgets.ForeignKeyWidget(Directory, 'name')
    )
    used_parts = fields.Field(
        attribute='used_parts',
        column_name='Используемые запасные части'
    )
    recovery_date = fields.Field(
        attribute='recovery_date',
        column_name='Дата восстановления'
    )
    downtime = fields.Field(
        attribute='downtime',
        column_name='Время простоя техники'
    )
    class Meta:
        model = Claim
        import_id_fields = ['machine', 'failure_date', 'failed_unit']

@admin.register(Claim)
class ClaimAdmin(ImportExportModelAdmin):
    form = ClaimForm
    resource_class = ClaimResource
    list_display = (
        'machine', 'failure_date', 'operating_time', 'failed_unit',
        'failure_description', 'recovery_method', 'used_parts',
        'recovery_date', 'downtime', 'service_company'
    )
    search_fields = ('machine__serial_number',)
    list_filter = ('failed_unit', 'recovery_method', 'service_company', 'failure_date')
    autocomplete_fields = ['machine', 'failed_unit', 'recovery_method', 'service_company']
    fieldsets = (
        (None, {
            'fields': (
                'machine', 'failure_date', 'operating_time', 'failed_unit',
                'failure_description', 'recovery_method', 'used_parts',
                'recovery_date', 'downtime', 'service_company'
            )
        }),
    )