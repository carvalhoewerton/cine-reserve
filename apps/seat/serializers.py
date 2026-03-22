from rest_framework import serializers

from apps.seat.models import Seat

class SeatSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()

    class Meta:
        model = Seat
        fields = ('id', 'row', 'number', 'label', 'status')

    def get_label(self, obj):
        return f'{obj.row}{obj.number}'