from rest_framework import serializers

from django_handleref.models import HandleRefModel


class HandleRefSerializer(serializers.ModelSerializer):
    version = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()

    class Meta:
        model = HandleRefModel
        fields = ["created", "updated", "status"]
