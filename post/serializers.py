from rest_framework import serializers
from post.models import Stream, Tag

class StreamSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()
    post = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='postcomment',
        lookup_field='id',
        lookup_url_kwarg='post_id',
    )

    class Meta:
        model = Stream
        fields = '__all__'
        depth = 1

class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        exclude = ['slug']
