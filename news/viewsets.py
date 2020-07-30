from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .serializers import NewsSerializer
from .models import News
from .permissions import NewsPermission
from .pagination import NewsPagination


class NewsViewSet(ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = (NewsPermission,)
    pagination_class = NewsPagination

    @action(methods=['get'], detail=False, url_path='important', url_name='important_news')
    def get_important_news(self, request, pk=None):
        important_news = self.queryset.filter(is_important=True)
        page = self.paginate_queryset(important_news)
        if page:
            return self.get_paginated_response(self.serializer_class(page, many=True).data)
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
