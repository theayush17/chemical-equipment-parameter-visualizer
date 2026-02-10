
from rest_framework import serializers
from .models import UploadRecord

class UploadRecordSerializer(serializers.ModelSerializer):
    total_count = serializers.ReadOnlyField(source='summary_json.total_count')
    avg_flowrate = serializers.ReadOnlyField(source='summary_json.avg_flowrate')
    avg_pressure = serializers.ReadOnlyField(source='summary_json.avg_pressure')
    avg_temperature = serializers.ReadOnlyField(source='summary_json.avg_temperature')
    type_distribution = serializers.ReadOnlyField(source='summary_json.type_distribution')

    class Meta:
        model = UploadRecord
        fields = ['id', 'filename', 'timestamp', 'total_count', 'avg_flowrate', 
                  'avg_pressure', 'avg_temperature', 'type_distribution']
