from django_syncref.models import SyncRefModel
from rest_framework import serializers

class SyncRefSerializer(serializers.ModelSerializer):
  version = serializers.ReadOnlyField()
  class Meta:
    model = SyncRefModel,
    fields = [
      'created',
      'updated',
      'status',
      'version',
    ]
