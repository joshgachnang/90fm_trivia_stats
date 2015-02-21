from django.contrib.auth.models import User
from rest_framework import viewsets
from website.models import ScoreSerializer, SMSSubscriberSerializer, \
    EmailSubscriberSerializer, Score, SMSSubscriber, EmailSubscriber, \
    UserSerializer


class ScoreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Score.objects.all()
    serializer_class = ScoreSerializer


class SMSSubscriberViewSet(viewsets.ModelViewSet):
    queryset = SMSSubscriber.objects.all()
    serializer_class = SMSSubscriberSerializer


class EmailSubscriberViewSet(viewsets.ModelViewSet):
    queryset = EmailSubscriber.objects.all()
    serializer_class = EmailSubscriberSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer