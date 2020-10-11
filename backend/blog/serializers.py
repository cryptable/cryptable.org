from rest_framework import serializers
from blog.models import Article
from django.contrib.auth.models import User


class ArticlesSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Article
        fields = ['url', 'slug', 'title', 'summary', 'article', 'created', 'updated', 'owner']
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class UserArticlesSerializer(serializers.ModelSerializer):
    articles = serializers.HyperlinkedRelatedField(many=True, view_name='article-detail', read_only=True)

    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'snippets']