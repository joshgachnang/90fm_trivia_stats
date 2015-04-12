import logging

from rest_framework import filters
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from website.models import ScoreSerializer, \
    TeamListSerializer, Score, SubscriberSerializer, Subscriber

logger = logging.getLogger('django')


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


class SubscriberViewSet(viewsets.ModelViewSet):
    queryset = Subscriber.objects.all()
    serializer_class = SubscriberSerializer


@api_view(http_method_names=['POST'])
def unsubscribe(request):
    logger.info('Unsubscribe request for {}'.format(request.data))
    if request.data.get('email'):
        emails = Subscriber.objects.filter(email=request.data.get('email'))
    else:
        emails = Subscriber.objects.none()
    if request.data.get('phoneNumber'):
        phones = Subscriber.objects.filter(
            phone_number=request.data.get('phoneNumber'))
    else:
        phones = Subscriber.objects.none()
    if emails.count() == 0 and phones.count == 0:
        return Response({"message": "No matching subscribers. Are you sure "
                                    "you typed it correctly?"},
                        status=status.HTTP_404_NOT_FOUND)
    logger.info('Unsubscribing: {}'.format(phones))
    phones.delete()
    logger.info('Unsubscribing: {}'.format(emails))
    emails.delete()
    return Response({"message": "Unsubscribed"})
