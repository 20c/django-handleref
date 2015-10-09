from django_handleref.models import HandleRefModel
from rest_framework import serializers

class HandleRefSerializer(serializers.ModelSerializer):
  version = serializers.ReadOnlyField()
  class Meta:
    model = HandleRefModel,
    fields = [
      'created',
      'updated',
      'status'
    ]
