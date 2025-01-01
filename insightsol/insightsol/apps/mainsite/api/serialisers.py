from rest_framework import serializers

class BookSerializer(serializers.Serializer):
    title = serializers.CharField()
    author_name = serializers.ListField(child=serializers.CharField())
    languages = serializers.ListField(child=serializers.CharField())
    available_formats = serializers.ListField(child=serializers.CharField())
    download_count = serializers.IntegerField()
