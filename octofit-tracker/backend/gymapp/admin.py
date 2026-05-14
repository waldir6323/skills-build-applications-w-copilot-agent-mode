from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    ActivityLog,
    ClientRecord,
    GymUser,
    InstructorProfile,
    Product,
    Team,
    TrainingSuggestion,
    StudentProfile,
)


@admin.register(GymUser)
class GymUserAdmin(UserAdmin):
    model = GymUser
    list_display = ('email', 'full_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('email', 'full_name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('full_name', 'role')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'role', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'fitness_level', 'enrollment_date')
    search_fields = ('user__email', 'user__full_name', 'fitness_level')


@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'certification', 'specialty')
    search_fields = ('user__email', 'user__full_name', 'certification', 'specialty')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'inventory', 'active')
    list_filter = ('active',)
    search_fields = ('name',)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'coach', 'goal', 'active', 'created_at')
    filter_horizontal = ('members',)
    search_fields = ('name', 'coach__email', 'coach__full_name')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'duration_minutes', 'intensity', 'points', 'activity_date')
    list_filter = ('activity_type', 'intensity')
    search_fields = ('user__email', 'user__full_name')


@admin.register(TrainingSuggestion)
class TrainingSuggestionAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'recommended_activity', 'created_at')
    search_fields = ('user__email', 'user__full_name', 'title')


@admin.register(ClientRecord)
class ClientRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'membership_status', 'join_date', 'last_visit')
    search_fields = ('user__email', 'user__full_name', 'membership_status')
