from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.db.models import Sum


class GymUserManager(BaseUserManager):
    def create_user(self, email, password=None, role='student', **extra_fields):
        if not email:
            raise ValueError('El usuario debe tener un correo electrónico')
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuario debe tener is_superuser=True.')
        return self.create_user(email, password, role='instructor', **extra_fields)


class GymUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('student', 'Estudiante'),
        ('instructor', 'Profesor'),
    ]

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    objects = GymUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return f'{self.full_name} ({self.get_role_display()})'

    @property
    def total_points(self):
        return self.activity_logs.aggregate(total=Sum('points'))['total'] or 0

    @property
    def team_names(self):
        return [team.name for team in self.teams.all()]


class StudentProfile(models.Model):
    user = models.OneToOneField(GymUser, on_delete=models.CASCADE, related_name='student_profile')
    enrollment_date = models.DateField(null=True, blank=True)
    fitness_level = models.CharField(max_length=50, blank=True)
    goals = models.TextField(blank=True)

    def __str__(self):
        return f'Perfil de estudiante: {self.user.full_name}'


class InstructorProfile(models.Model):
    user = models.OneToOneField(GymUser, on_delete=models.CASCADE, related_name='instructor_profile')
    certification = models.CharField(max_length=120, blank=True)
    specialty = models.CharField(max_length=120, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f'Perfil de profesor: {self.user.full_name}'


class Product(models.Model):
    name = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    inventory = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    coach = models.ForeignKey(GymUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='coached_teams')
    members = models.ManyToManyField(GymUser, related_name='teams', blank=True)
    goal = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def total_points(self):
        return self.activities.aggregate(total=Sum('points'))['total'] or 0


class ActivityLog(models.Model):
    ACTIVITY_CHOICES = [
        ('cardio', 'Cardio'),
        ('strength', 'Fuerza'),
        ('flexibility', 'Flexibilidad'),
        ('mobility', 'Movilidad'),
    ]

    INTENSITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
    ]

    user = models.ForeignKey(GymUser, on_delete=models.CASCADE, related_name='activity_logs')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True, related_name='activities')
    activity_date = models.DateField(auto_now_add=True)
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_CHOICES)
    duration_minutes = models.PositiveIntegerField(default=0)
    intensity = models.CharField(max_length=20, choices=INTENSITY_CHOICES, default='medium')
    calories_burned = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    points = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        intensity_weight = {'low': 1, 'medium': 2, 'high': 3}.get(self.intensity, 1)
        type_bonus = {'cardio': 2, 'strength': 3, 'flexibility': 1, 'mobility': 1}.get(self.activity_type, 1)
        self.points = max(0, self.duration_minutes * intensity_weight + type_bonus)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.full_name} - {self.activity_type} ({self.activity_date})'


class TrainingSuggestion(models.Model):
    user = models.ForeignKey(GymUser, on_delete=models.CASCADE, related_name='training_suggestions')
    title = models.CharField(max_length=180)
    description = models.TextField()
    target_fitness_level = models.CharField(max_length=100, blank=True)
    recommended_activity = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Sugerencia para {self.user.full_name}: {self.title}'

    @classmethod
    def generate_for_user(cls, user):
        fitness_level = getattr(user.student_profile, 'fitness_level', '').lower()
        if 'beginner' in fitness_level or not fitness_level:
            title = 'Comienza con una base sólida'
            description = (
                'Haz entrenamientos de movilidad ligera y cardio moderado tres veces por semana. '
                'Concéntrate en la forma y en ganar consistencia antes de subir la intensidad.'
            )
            recommended_activity = 'Cardio ligero + movilidad'
            target_fitness_level = 'Beginner'
        elif 'intermediate' in fitness_level:
            title = 'Mejora tu resistencia y fuerza'
            description = (
                'Añade entrenamientos de fuerza con intervalos de cardio para aumentar tu capacidad. '
                'Asegúrate de tomar descansos activos entre series y medir tu progreso cada semana.'
            )
            recommended_activity = 'Fuerza con intervalos'
            target_fitness_level = 'Intermediate'
        else:
            title = 'Afinar rendimiento avanzado'
            description = (
                'Combina sesiones de alta intensidad con ejercicios de flexibilidad para reducir fatiga. '
                'Monitorea tus tiempos y ajusta el volumen según tu recuperación.'
            )
            recommended_activity = 'Entrenamiento HIIT y flexibilidad'
            target_fitness_level = fitness_level.title() or 'Avanzado'

        suggestion = cls.objects.create(
            user=user,
            title=title,
            description=description,
            target_fitness_level=target_fitness_level,
            recommended_activity=recommended_activity,
        )
        return suggestion


class ClientRecord(models.Model):
    user = models.ForeignKey(GymUser, on_delete=models.CASCADE, related_name='client_records')
    membership_status = models.CharField(max_length=80, default='Activo')
    join_date = models.DateField(auto_now_add=True)
    last_visit = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f'Registro de cliente: {self.user.full_name}'
