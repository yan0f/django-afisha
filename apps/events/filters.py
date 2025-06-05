from django.contrib.postgres.search import SearchQuery, SearchVector
from django.db.models import Count, F, Q, QuerySet
from django_filters import rest_framework as filters

from apps.events.models import Event
from apps.tags.models import Tag


class EventFilter(filters.FilterSet):
    has_free_seats = filters.BooleanFilter(method='filter_by_free_seats')
    date = filters.DateFilter(field_name='start_time', lookup_expr='date')
    description = filters.CharFilter(method='filter_description')
    tags = filters.ModelMultipleChoiceFilter(queryset=Tag.objects.all(), field_name='tags', method='filter_by_tags')

    class Meta:
        model = Event
        fields = ['location', 'status', 'has_free_seats', 'date']

    def filter_by_free_seats(self, queryset: QuerySet, _: str, value: bool) -> QuerySet:
        queryset = queryset.annotate(booked_count=Count('booking'))
        if value:
            return queryset.filter(booked_count__lt=F('seats_number'))
        else:
            return queryset.filter(booked_count__gte=F('seats_number'))

    def filter_description(self, _: QuerySet, __: str, value: str) -> QuerySet:
        vector = SearchVector('description', config='russian')
        query = SearchQuery(value, config='russian')
        return Event.objects.annotate(search=vector).filter(search=query)

    def filter_by_tags(self, queryset: QuerySet, _: str, value: list) -> QuerySet:
        if value:
            queryset = (
                queryset.filter(tags__in=value)
                .annotate(tags_count=Count('tags', filter=Q(tags__in=value)))
                .order_by('-tags_count')
            )

        return queryset
