from rest_framework import serializers
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


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ['enrollment_date', 'fitness_level', 'goals']


class InstructorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstructorProfile
        fields = ['certification', 'specialty', 'bio']


class GymUserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymUser
        fields = ['id', 'email', 'full_name', 'role']


class TeamSerializer(serializers.ModelSerializer):
    coach = GymUserBasicSerializer(read_only=True)
    coach_id = serializers.PrimaryKeyRelatedField(
        queryset=GymUser.objects.filter(role='instructor'),
        write_only=True,
        source='coach',
        required=False,
        allow_null=True,
    )
    members = GymUserBasicSerializer(many=True, read_only=True)
    member_ids = serializers.PrimaryKeyRelatedField(
        queryset=GymUser.objects.filter(role='student'),
        many=True,
        write_only=True,
        source='members',
        required=False,
    )
    total_points = serializers.IntegerField(read_only=True, source='total_points')

    class Meta:
        model = Team
        fields = [
            'id',
            'name',
            'description',
            'coach',
            'coach_id',
            'members',
            'member_ids',
            'goal',
            'active',
            'created_at',
            'total_points',
        ]

    def create(self, validated_data):
        members = validated_data.pop('members', [])
        team = super().create(validated_data)
        team.members.set(members)
        return team


class ActivityLogSerializer(serializers.ModelSerializer):
    user = GymUserBasicSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=GymUser.objects.filter(role='student'),
        write_only=True,
        source='user',
    )
    team = TeamSerializer(read_only=True)
    team_id = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
        write_only=True,
        source='team',
        required=False,
        allow_null=True,
    )

    class Meta:
        model = ActivityLog
        fields = [
            'id',
            'user',
            'user_id',
            'team',
            'team_id',
            'activity_date',
            'activity_type',
            'duration_minutes',
            'intensity',
            'calories_burned',
            'notes',
            'points',
        ]
        read_only_fields = ['activity_date', 'points']


class TrainingSuggestionSerializer(serializers.ModelSerializer):
    user = GymUserBasicSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=GymUser.objects.filter(role='student'),
        write_only=True,
        source='user',
    )

    class Meta:
        model = TrainingSuggestion
        fields = [
            'id',
            'user',
            'user_id',
            'title',
            'description',
            'target_fitness_level',
            'recommended_activity',
            'created_at',
        ]
        read_only_fields = ['created_at']


class GymUserSerializer(serializers.ModelSerializer):
    student_profile = StudentProfileSerializer(required=False)
    instructor_profile = InstructorProfileSerializer(required=False)
    team_names = serializers.ListField(child=serializers.CharField(), read_only=True, source='team_names')
    total_points = serializers.IntegerField(read_only=True, source='total_points')

    class Meta:
        model = GymUser
        fields = [
            'id',
            'email',
            'full_name',
            'role',
            'joined_at',
            'student_profile',
            'instructor_profile',
            'team_names',
            'total_points',
            'password',
        ]
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

    def create(self, validated_data):
        profile_data = {}
        if 'student_profile' in validated_data:
            profile_data = validated_data.pop('student_profile')
        if 'instructor_profile' in validated_data:
            profile_data = validated_data.pop('instructor_profile')

        password = validated_data.pop('password')
        user = GymUser.objects.create_user(password=password, **validated_data)

        if user.role == 'student' and profile_data:
            StudentProfile.objects.create(user=user, **profile_data)
        elif user.role == 'instructor' and profile_data:
            InstructorProfile.objects.create(user=user, **profile_data)

        return user


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'inventory', 'active']


class ClientRecordSerializer(serializers.ModelSerializer):
    user = GymUserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=GymUser.objects.all(), write_only=True, source='user')

    class Meta:
        model = ClientRecord
        fields = ['id', 'user', 'user_id', 'membership_status', 'join_date', 'last_visit', 'notes']
