from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    ActivityLog,
    ClientRecord,
    GymUser,
    Product,
    Team,
    TrainingSuggestion,
)
from .serializers import (
    ActivityLogSerializer,
    ClientRecordSerializer,
    GymUserSerializer,
    ProductSerializer,
    TeamSerializer,
    TrainingSuggestionSerializer,
)


class GymUserViewSet(viewsets.ModelViewSet):
    queryset = GymUser.objects.annotate(total_points=Sum('activity_logs__points')).order_by('-joined_at')
    serializer_class = GymUserSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ClientRecordViewSet(viewsets.ModelViewSet):
    queryset = ClientRecord.objects.all().order_by('-join_date')
    serializer_class = ClientRecordSerializer


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all().order_by('-created_at')
    serializer_class = TeamSerializer


class ActivityLogViewSet(viewsets.ModelViewSet):
    queryset = ActivityLog.objects.all().order_by('-activity_date')
    serializer_class = ActivityLogSerializer


class TrainingSuggestionViewSet(viewsets.ModelViewSet):
    queryset = TrainingSuggestion.objects.all().order_by('-created_at')
    serializer_class = TrainingSuggestionSerializer

    @action(detail=False, methods=['post'], url_path='generate')
    def generate(self, request):
        user_id = request.data.get('user_id')
        user = get_object_or_404(GymUser, id=user_id, role='student')
        suggestion = TrainingSuggestion.generate_for_user(user)
        serializer = self.get_serializer(suggestion)
        return Response(serializer.data)


class LeaderboardView(APIView):
    def get(self, request):
        students = (
            GymUser.objects.filter(role='student')
            .annotate(total_points=Sum('activity_logs__points'))
            .order_by('-total_points', 'full_name')[:20]
        )
        leaderboard = [
            {
                'id': student.id,
                'full_name': student.full_name,
                'total_points': student.total_points or 0,
                'team_names': student.team_names,
            }
            for student in students
        ]
        return Response(leaderboard)
