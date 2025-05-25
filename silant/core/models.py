from django.db import models
from django.contrib.auth.models import AbstractUser


class Directory(models.Model):
    entity_name = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.entity_name}: {self.name}"

# Пользователь с ролями
class User(AbstractUser):
    ROLE_CHOICES = [
        ('guest', 'Гость'),
        ('client', 'Клиент'),
        ('service', 'Сервисная организация'),
        ('manager', 'Менеджер'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='guest')


class Machine(models.Model):
    # --- поля, связанные со справочником ---
    model = models.ForeignKey(
        Directory, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='machines_model',
        limit_choices_to={'entity_name': 'Модель техники'},
        verbose_name='Модель техники'
    )
    engine_model = models.ForeignKey(
        Directory, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='machines_engine_model',
        limit_choices_to={'entity_name': 'Модель двигателя'},
        verbose_name='Модель двигателя'
    )
    transmission_model = models.ForeignKey(
        Directory, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='machines_transmission_model',
        limit_choices_to={'entity_name': 'Модель трансмиссии'},
        verbose_name='Модель трансмиссии'
    )
    drive_axle_model = models.ForeignKey(
        Directory, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='machines_drive_axle_model',
        limit_choices_to={'entity_name': 'Модель ведущего моста'},
        verbose_name='Модель ведущего моста'
    )
    steer_axle_model = models.ForeignKey(
        Directory, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='machines_steer_axle_model',
        limit_choices_to={'entity_name': 'Модель управляемого моста'},
        verbose_name='Модель управляемого моста'
    )
    # --- поля со свободным вводом ---
    serial_number = models.CharField(max_length=50, unique=True, verbose_name='Зав. № машины')
    engine_serial = models.CharField(max_length=50, verbose_name='Зав. № двигателя')
    transmission_serial = models.CharField(max_length=50, verbose_name='Зав. № трансмиссии')
    drive_axle_serial = models.CharField(max_length=50, verbose_name='Зав. № ведущего моста')
    steer_axle_serial = models.CharField(max_length=50, verbose_name='Зав. № управляемого моста')
    contract = models.CharField(max_length=200, blank=True, verbose_name='Договор поставки №, дата')
    shipment_date = models.DateField(verbose_name='Дата отгрузки с завода')
    client = models.CharField(max_length=200, verbose_name='Покупатель')
    consignee = models.CharField(max_length=200, verbose_name='Грузополучатель (конечный потребитель)')
    delivery_address = models.CharField(max_length=300, verbose_name='Адрес поставки (эксплуатации)')
    equipment = models.TextField(verbose_name='Комплектация (доп. опции)')
    service_company = models.CharField(max_length=200, blank=True, verbose_name='Сервисная компания')
    # --- связь с пользователями ---
    client_user = models.ForeignKey(
        User, related_name='client_machines', null=True, blank=True, on_delete=models.SET_NULL,
        limit_choices_to={'role': 'client'}, verbose_name='Клиент'
    )
    service_user = models.ForeignKey(
        User, related_name='service_machines', null=True, blank=True, on_delete=models.SET_NULL,
        limit_choices_to={'role': 'service'}, verbose_name='Сервисная компания'
    )

    def __str__(self):
        return f"{self.model} ({self.serial_number})"

# --- ТО (техническое обслуживание) ---
class Maintenance(models.Model):
    machine = models.ForeignKey(Machine, related_name='maintenances', on_delete=models.CASCADE)
    maintenance_type = models.ForeignKey(
        Directory, on_delete=models.SET_NULL, null=True, blank=True,
        limit_choices_to={'entity_name': 'Вид ТО'},
        related_name='maintenances_type',  # <--- исправлено
        verbose_name='Вид ТО'
    )
    date = models.DateField(verbose_name='Дата проведения ТО')
    operating_time = models.IntegerField(verbose_name='Наработка, м/час')
    order_number = models.CharField(max_length=50, verbose_name='№ заказ-наряда')
    order_date = models.DateField(verbose_name='Дата заказ-наряда')
    service_company = models.ForeignKey(
        Directory, on_delete=models.SET_NULL, null=True, blank=True,
        limit_choices_to={'entity_name': 'Сервисная компания'},
        related_name='maintenances_service_company',  # <--- исправлено
        verbose_name='Организация, проводившая ТО'
    )

    def __str__(self):
        return f"{self.machine.serial_number} - {self.maintenance_type} ({self.date})"

# --- Рекламация ---
class Claim(models.Model):
    machine = models.ForeignKey(Machine, related_name='claims', on_delete=models.CASCADE)
    failure_date = models.DateField(verbose_name='Дата отказа')
    operating_time = models.IntegerField(verbose_name='Наработка, м/час')
    failed_unit = models.ForeignKey(
        Directory, on_delete=models.SET_NULL, null=True, blank=True,
        limit_choices_to={'entity_name': 'Узел отказа'},
        related_name='claims_failed_unit',  # <--- исправлено
        verbose_name='Узел отказа'
    )
    failure_description = models.TextField(verbose_name='Описание отказа')
    recovery_method = models.ForeignKey(
        Directory, on_delete=models.SET_NULL, null=True, blank=True,
        limit_choices_to={'entity_name': 'Способ восстановления'},
        related_name='claims_recovery_method',  # <--- исправлено
        verbose_name='Способ восстановления'
    )
    used_parts = models.TextField(blank=True, verbose_name='Используемые запасные части')
    recovery_date = models.DateField(verbose_name='Дата восстановления')
    downtime = models.IntegerField(verbose_name='Время простоя техники (дни)')
    service_company = models.ForeignKey(
        Directory, on_delete=models.SET_NULL, null=True, blank=True,
        limit_choices_to={'entity_name': 'Сервисная компания'},
        related_name='claims_service_company',  # <--- исправлено
        verbose_name='Сервисная компания'
    )

    def __str__(self):
        return f"{self.machine.serial_number} - {self.failed_unit} ({self.failure_date})"

