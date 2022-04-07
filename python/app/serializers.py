from rest_framework import serializers

from .models import *

class CustomerFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerFile
        fields = "__all__"