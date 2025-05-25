from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Machine, Maintenance, Claim, Directory
from .serializers import MachineSerializer, MaintenanceSerializer, ClaimSerializer, DirectorySerializer
from .forms import MachineForm, MaintenanceForm, ClaimForm
from .decorators import role_required

# ---- REST API ----

class MachineViewSet(viewsets.ModelViewSet):
    """
    API endpoint для работы с машинами (таблица «Машина»).

    list:
    Получить список всех машин, доступных пользователю.
    Доступно менеджеру (все машины), сервисной компании (только свои), клиенту (только свои).
    Поддерживаются фильтры: модель техники, модель двигателя, модель трансмиссии, ведущий мост, управляемый мост, заводской номер.
    По умолчанию сортировка по дате отгрузки с завода (shipment_date).
    Пример запроса:
        GET /api/machines/?model=3&ordering=-shipment_date

    retrieve:
    Получить подробную информацию о конкретной машине по id.
    Пример запроса:
        GET /api/machines/5/

    create:
    Добавить новую машину (только для менеджера).
    Пример запроса:
        POST /api/machines/
            {
                "serial_number": "12345",
                "model": 3,
                "engine_model": 2,
                ...
            }

        update:
    Изменить существующую машину (только для менеджера).

        partial_update:
    Частично изменить существующую машину (только для менеджера).

        destroy:
        Удалить машину (только для менеджера).
        """
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = [
        'model', 'engine_model', 'transmission_model',
        'steer_axle_model', 'drive_axle_model', 'serial_number'
    ]
    ordering_fields = [
        'shipment_date', 'model', 'engine_model',
        'transmission_model', 'steer_axle_model', 'drive_axle_model'
    ]
    ordering = ['-shipment_date']
    search_fields = [
        'model__name', 'engine_model__name', 'transmission_model__name',
        'steer_axle_model__name', 'drive_axle_model__name', 'serial_number'
    ]

    def get_queryset(self):
        """
        Фильтрация по ролям пользователя:
        - Менеджер: все машины.
        - Клиент: только свои машины.
        - Сервисная компания: только свои машины.
        - Гость: пусто.
        """
        user = self.request.user
        if not user.is_authenticated or user.role == 'guest':
            return Machine.objects.none()
        elif user.role == 'client':
            return Machine.objects.filter(client_user=user)
        elif user.role == 'service':
            return Machine.objects.filter(service_user=user)
        elif user.role == 'manager':
            return Machine.objects.all()
        return Machine.objects.none()

    def get_permissions(self):
        """
        Ограничение доступа к методам по ролям.
        - Менеджер: полный доступ.
        - Сервисная компания/Клиент: только просмотр.
        """
        user = self.request.user
        if not user.is_authenticated or user.role == 'guest':
            return [permissions.IsAuthenticated()]
        elif user.role == 'manager':
            return [permissions.IsAuthenticated()]
        elif user.role == 'service':
            if self.action in ['create', 'update', 'partial_update', 'destroy']:
                return [permissions.IsAdminUser()]
            return [permissions.IsAuthenticated()]
        elif user.role == 'client':
            if self.action in ['create', 'update', 'partial_update', 'destroy']:
                return [permissions.IsAdminUser()]
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

class MaintenanceViewSet(viewsets.ModelViewSet):
    """
    API endpoint для работы с ТО (таблица «ТО»).

        list:
        Получить список всех ТО, доступных пользователю.
        Поддерживаются фильтры: вид ТО, заводской номер машины, сервисная компания.
        По умолчанию сортировка по дате проведения ТО (date).
        Пример запроса:
            GET /api/maintenances/?maintenance_type=2&ordering=-date

        retrieve:
        Получить подробную информацию о конкретном ТО по id.
        Пример запроса:
            GET /api/maintenances/10/

        create:
        Добавить запись о ТО (доступно менеджеру, сервисной компании, клиенту).

        update:
        Изменить запись о ТО.

        partial_update:
        Частично изменить запись о ТО.

        destroy:
        Удалить запись о ТО.
        """
    queryset = Maintenance.objects.all()
    serializer_class = MaintenanceSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = {
        'maintenance_type': ['exact'],
        'machine__serial_number': ['exact', 'icontains'],
        'service_company': ['exact', 'icontains'],
    }
    ordering_fields = ['date', 'maintenance_type', 'service_company']
    ordering = ['-date']
    search_fields = ['maintenance_type__name', 'machine__serial_number', 'service_company__name']

    def get_queryset(self):
        """
        Фильтрация по ролям пользователя:
        - Менеджер: все ТО.
        - Клиент: только ТО своих машин.
        - Сервисная компания: только ТО своих машин.
        - Гость: пусто.
        """
        user = self.request.user
        if not user.is_authenticated or user.role == 'guest':
            return Maintenance.objects.none()
        elif user.role == 'client':
            return Maintenance.objects.filter(machine__client_user=user)
        elif user.role == 'service':
            return Maintenance.objects.filter(machine__service_user=user)
        elif user.role == 'manager':
            return Maintenance.objects.all()
        return Maintenance.objects.none()

    def get_permissions(self):
        """
        Ограничение доступа к методам по ролям.
        """
        user = self.request.user
        if not user.is_authenticated or user.role == 'guest':
            return [permissions.IsAuthenticated()]
        elif user.role == 'manager':
            return [permissions.IsAuthenticated()]
        elif user.role == 'service':
            if self.action in ['create', 'update', 'partial_update', 'destroy']:
                return [permissions.IsAdminUser()]
            return [permissions.IsAuthenticated()]
        elif user.role == 'client':
            if self.action in ['create', 'update', 'partial_update', 'destroy']:
                return [permissions.IsAdminUser()]
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

class ClaimViewSet(viewsets.ModelViewSet):
    """
        API endpoint для работы с рекламациями (таблица «Рекламации»).

        list:
        Получить список всех рекламаций, доступных пользователю.
        Поддерживаются фильтры: узел отказа, способ восстановления, заводской номер машины, сервисная компания.
        По умолчанию сортировка по дате отказа (failure_date).
        Пример запроса:
            GET /api/claims/?failed_unit=3&ordering=-failure_date

        retrieve:
        Получить подробную информацию о конкретной рекламации по id.
        Пример запроса:
            GET /api/claims/7/

        create:
        Добавить новую рекламацию (доступно менеджеру, сервисной компании).

        update:
        Изменить рекламацию.

        partial_update:
        Частично изменить рекламацию.

        destroy:
        Удалить рекламацию.
        """
    queryset = Claim.objects.all()
    serializer_class = ClaimSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = {
        'failed_unit': ['exact', 'icontains'],
        'recovery_method': ['exact', 'icontains'],
        'machine__serial_number': ['exact', 'icontains'],
        'service_company': ['exact', 'icontains'],
    }
    ordering_fields = ['failure_date', 'failed_unit', 'recovery_method']
    ordering = ['-failure_date']
    search_fields = ['failed_unit__name', 'recovery_method__name', 'machine__serial_number', 'service_company__name']

    def get_queryset(self):
        """
        Фильтрация по ролям пользователя:
        - Менеджер: все рекламации.
        - Клиент: только по своим машинам.
        - Сервисная компания: только по своим машинам.
        - Гость: пусто.
        """
        user = self.request.user
        if not user.is_authenticated or user.role == 'guest':
            return Claim.objects.none()
        elif user.role == 'client':
            return Claim.objects.filter(machine__client_user=user)
        elif user.role == 'service':
            return Claim.objects.filter(machine__service_user=user)
        elif user.role == 'manager':
            return Claim.objects.all()
        return Claim.objects.none()

    def get_permissions(self):
        """
        Ограничение доступа к методам по ролям.
        """
        user = self.request.user
        if not user.is_authenticated or user.role == 'guest':
            return [permissions.IsAuthenticated()]
        elif user.role == 'manager':
            return [permissions.IsAuthenticated()]
        elif user.role == 'service':
            if self.action in ['create', 'update', 'partial_update', 'destroy']:
                return [permissions.IsAdminUser()]
            return [permissions.IsAuthenticated()]
        elif user.role == 'client':
            if self.action in ['create', 'update', 'partial_update', 'destroy']:
                return [permissions.IsAdminUser()]
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

class DirectoryViewSet(viewsets.ModelViewSet):
    """
        API endpoint для работы со справочниками (таблица «Справочник»).

        list:
        Получить список всех элементов справочников.
        Можно фильтровать по названию справочника (entity_name) и названию элемента (name).
        По умолчанию сортировка по названию справочника и названию элемента.
        Пример запроса:
            GET /api/directories/?entity_name=Модель%20техники

        retrieve:
        Получить подробную информацию о конкретном элементе справочника по id.
        Пример запроса:
            GET /api/directories/12/

        create:
        Добавить новый элемент в справочник (доступно только менеджеру).
        Пример запроса:
            POST /api/directories/
            {
                "entity_name": "Модель техники",
                "name": "Погрузчик 5т",
                "description": "Описание модели"
            }

        update:
        Изменить существующий элемент справочника (только для менеджера).

        partial_update:
        Частично изменить элемент справочника (только для менеджера).

        destroy:
        Удалить элемент справочника (только для менеджера).
        """
    queryset = Directory.objects.all()
    serializer_class = DirectorySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['entity_name', 'name']
    ordering_fields = ['entity_name', 'name', 'description']
    ordering = ['entity_name', 'name']
    search_fields = ['name', 'description']

    def get_permissions(self):
        """
        Ограничение доступа:
        - Только менеджер может создавать, изменять и удалять элементы справочника.
        - Остальные пользователи могут только просматривать.
        """
        user = self.request.user
        if user.is_authenticated and user.role == 'manager':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

# ---- Публичная страница поиска (гость) ----

def public_search_page(request):
    """
    Публичная страница поиска по заводскому номеру для гостей (анонимных и авторизованных с ролью 'гость').
    """
    if request.user.is_authenticated and getattr(request.user, 'role', None) != 'guest':
        return redirect('dashboard')
    serial_number = request.GET.get('serial_number', '').strip()
    machine = None
    search = False

    if serial_number:
        search = True
        try:
            machine = Machine.objects.get(serial_number=serial_number)
        except Machine.DoesNotExist:
            machine = None
    machine_fields = None
    if machine:
        machine_fields = {
            'model': machine.model.name if machine.model else '',
            'serial_number': machine.serial_number,
            'engine_model': machine.engine_model.name if machine.engine_model else '',
            'engine_serial': machine.engine_serial,
            'transmission_model': machine.transmission_model.name if machine.transmission_model else '',
            'transmission_serial': machine.transmission_serial,
            'drive_axle_model': machine.drive_axle_model.name if machine.drive_axle_model else '',
            'drive_axle_serial': machine.drive_axle_serial,
            'steer_axle_model': machine.steer_axle_model.name if machine.steer_axle_model else '',
            'steer_axle_serial': machine.steer_axle_serial,
        }
    context = {
        'machine_fields': machine_fields,
        'search': search,
        'serial_number': serial_number,
    }
    return render(request, 'core/public_search.html', context)

# ---- Внутренние страницы для авторизованных пользователей ----

@login_required
def dashboard(request):
    user = request.user
    tab = request.GET.get('tab', 'info')
    selected_machine_id = request.GET.get('machine_id')
    ordering = request.GET.get('ordering')

    filters = {}
    for field in ['model', 'engine_model', 'transmission_model', 'steer_axle_model', 'drive_axle_model', 'serial_number']:
        value = request.GET.get(field)
        if value:
            filters[f"{field}"] = value

    if not user.is_authenticated or getattr(user, 'role', None) == 'guest':

        if request.method == 'GET' and 'serial_number' in request.GET:
            serial = request.GET['serial_number']
            machine = Machine.objects.filter(serial_number=serial).first()
            return render(request, 'core/public_search.html', {'machine': machine, 'serial_number': serial})
        return render(request, 'core/public_search.html')

    if user.role == 'manager':
        machines = Machine.objects.filter(**filters)
    elif user.role == 'client':
        machines = Machine.objects.filter(client_user=user, **filters)
    elif user.role == 'service':
        machines = Machine.objects.filter(service_user=user, **filters)
    else:
        machines = Machine.objects.none()

    if tab == 'info':
        machines = machines.order_by(ordering or '-shipment_date')

    if selected_machine_id:
        selected_machine = get_object_or_404(Machine, pk=selected_machine_id)
    else:
        selected_machine = machines.first() if machines.exists() else None

    if tab == 'to' and selected_machine:
        maintenances = Maintenance.objects.filter(machine=selected_machine).order_by(ordering or '-date')
    else:
        maintenances = Maintenance.objects.none()

    if tab == 'claims' and selected_machine:
        claims = Claim.objects.filter(machine=selected_machine).order_by(ordering or '-failure_date')
    else:
        claims = Claim.objects.none()

    context = {
        'machines': machines,
        'tab': tab,
        'selected_machine': selected_machine,
        'maintenances': maintenances,
        'claims': claims,
        'user_role': user.role,
        'request': request,
    }
    return render(request, 'core/dashboard.html', context)

def machine_detail(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    user = request.user
    if not user.is_authenticated or (
        user.role == 'client' and machine.client_user != user
    ) or (
        user.role == 'service' and machine.service_user != user
    ):
        return redirect('public_search_page')
    return render(request, 'core/machine/machine_detail.html', {'machine': machine, 'user_role': user.role})

def maintenance_detail(request, pk):
    maintenance = get_object_or_404(Maintenance, pk=pk)
    return render(request, 'core/maintenance/maintenance_detail.html', {'maintenance': maintenance})

def claim_detail(request, pk):
    claim = get_object_or_404(Claim, pk=pk)
    return render(request, 'core/claim/claim_detail.html', {'claim': claim})

# ---- API для публичного поиска ----

@api_view(['GET'])
def public_machine_search(request):
    serial = request.GET.get('serial_number')
    if not serial:
        return Response({'error': 'Не указан заводской номер'}, status=400)
    try:
        machine = Machine.objects.get(serial_number=serial)
        data = {
            'model': machine.model.name if machine.model else '',
            'serial_number': machine.serial_number,
            'engine_model': machine.engine_model.name if machine.engine_model else '',
            'engine_serial': machine.engine_serial,
            'transmission_model': machine.transmission_model.name if machine.transmission_model else '',
            'transmission_serial': machine.transmission_serial,
            'drive_axle_model': machine.drive_axle_model.name if machine.drive_axle_model else '',
            'drive_axle_serial': machine.drive_axle_serial,
            'steer_axle_model': machine.steer_axle_model.name if machine.steer_axle_model else '',
            'steer_axle_serial': machine.steer_axle_serial,
        }
        return Response(data)
    except Machine.DoesNotExist:
        return Response({'error': 'Данных о машине с таким заводским номером нет в системе.'}, status=404)

# --- для машин, ТО, рекламаций (только для нужных ролей) ---

@login_required
@role_required('manager')
def machine_create(request):
    if request.method == 'POST':
        form = MachineForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = MachineForm()
    return render(request, 'core/machine/machine_form.html', {'form': form})

@login_required
@role_required('manager')
def machine_update(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    form = MachineForm(request.POST or None, instance=machine)
    if form.is_valid():
        form.save()
        return redirect('dashboard')
    return render(request, 'core/machine/machine_form.html', {'form': form})

@login_required
@role_required('manager', 'service', 'client')
def maintenance_create(request, machine_id=None):
    machine = get_object_or_404(Machine, pk=machine_id) if machine_id else None
    if request.method == 'POST':
        form = MaintenanceForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        if machine:
            form = MaintenanceForm(user=request.user, instance=Maintenance(machine=machine))
        else:
            form = MaintenanceForm(user=request.user)
    return render(request, 'core/maintenance/maintenance_form.html', {'form': form})

@login_required
@role_required('manager', 'service', 'client')
def maintenance_update(request, pk):
    maintenance = get_object_or_404(Maintenance, pk=pk)
    user = request.user
    if user.role == 'client' and maintenance.machine.client_user != user:
        return HttpResponseForbidden("Нет доступа")
    if user.role == 'service' and maintenance.machine.service_user != user:
        return HttpResponseForbidden("Нет доступа")
    form = MaintenanceForm(request.POST or None, instance=maintenance, user=request.user)
    if form.is_valid():
        form.save()
        return redirect('dashboard')
    return render(request, 'core/maintenance/maintenance_form.html', {'form': form})

@login_required
@role_required('manager', 'service')
def claim_create(request, machine_id=None):
    if request.method == 'POST':
        form = ClaimForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        initial = {}
        if machine_id:
            machine = get_object_or_404(Machine, pk=machine_id)
            initial['machine'] = machine
        form = ClaimForm(initial=initial, user=request.user)
    return render(request, 'core/claim/claim_form.html', {'form': form})

@login_required
@role_required('manager', 'service')
def claim_update(request, pk):
    claim = get_object_or_404(Claim, pk=pk)
    user = request.user
    if user.role == 'service' and claim.machine.service_user != user:
        return HttpResponseForbidden("Нет доступа")
    form = ClaimForm(request.POST or None, instance=claim, user=request.user)
    if form.is_valid():
        form.save()
        return redirect('dashboard')
    return render(request, 'core/claim/claim_form.html', {'form': form})
