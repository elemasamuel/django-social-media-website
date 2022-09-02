from cgitb import lookup
from rest_framework import serializers

from django.contrib.auth.models import User

from account.models import Profile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class HyperUserSerializer(serializers.ModelSerializer):
    favorites = serializers.HyperlinkedRelatedField(
        read_only=True,
        many=True,
        view_name='postcomment',
        lookup_field='id',
        lookup_url_kwarg='post_id')
    class Meta:
        model = Profile
        fields = '__all__'
        depth = 1

