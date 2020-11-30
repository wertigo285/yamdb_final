from django_filters import rest_framework as filters
from titles.models import Title, Genre


class TitleFilter(filters.FilterSet):
    category = filters.CharFilter(field_name='category__slug',lookup_expr='iexact')
    genre = filters.CharFilter(field_name='genre__slug',lookup_expr='iexact')
    name = filters.CharFilter(
        field_name='name', lookup_expr='icontains')
    year = filters.NumberFilter(
        field_name='year',lookup_expr='exact') 

    class Meta:
        model = Title
        fields = ['category','genre','name','year']
