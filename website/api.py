from django.contrib.auth.models import User
from rest_framework import filters
from rest_framework import viewsets
from website.models import ScoreSerializer, SMSSubscriberSerializer, \
    EmailSubscriberSerializer, Score, SMSSubscriber, EmailSubscriber, \
    UserSerializer, TeamListSerializer


class ScoreViewSet(viewsets.ReadOnlyModelViewSet):
    filter_fields = ('hour', 'year', 'team_name')
    search_fields = ('@team_name',)
    ordering_fields = ('score', 'year', 'team_name', 'hour', 'place')
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter,
                       filters.SearchFilter)
    queryset = Score.objects.all()
    serializer_class = ScoreSerializer


class TeamsList(viewsets.ReadOnlyModelViewSet):
    page_size = 10000
    max_page_size = 10000
    queryset = Score.objects.values('team_name').distinct()
    serializer_class = TeamListSerializer


class SMSSubscriberViewSet(viewsets.ModelViewSet):
    queryset = SMSSubscriber.objects.all()
    serializer_class = SMSSubscriberSerializer


class EmailSubscriberViewSet(viewsets.ModelViewSet):
    queryset = EmailSubscriber.objects.all()
    serializer_class = EmailSubscriberSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
