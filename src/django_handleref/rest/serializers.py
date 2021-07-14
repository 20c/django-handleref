from django_handleref.models import HandleRefModel
from rest_framework import serializers

class HandleRefSerializer(serializers.ModelSerializer):
    version = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()
    class Meta(object):
        model = HandleRefModel
        fields = [
            'created',
            'updated',
            'status'
        ]
