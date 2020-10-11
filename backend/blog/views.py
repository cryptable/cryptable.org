from blog.models import Article
from blog.serializers import ArticlesSerializer, UserArticlesSerializer
from blog.permissions import IsOwnerOrReadOnly
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.contrib.auth.models import User


class ArticleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for the blog articles, creates `list`, `create`, `retrieve`, `update` adn `destroy` actions.
    All using hyperlinked sets
    """
    queryset = Article.objects.all()
    serializer_class = ArticlesSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UserArticlesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewseet to show the articles of a user
    """
    queryset = User.objects.all()
    serializer_class = UserArticlesSerializer


@api_view(['GET'])
def api_root(request, format=None):
    """
    Render the root paths for the blog
    """
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'snippets': reverse('snippet-list', request=request, format=format),
    })
