from rest_framework.serializers import ModelSerializer, ValidationError

from apps.events.models import Event
from apps.tags.serializer import TagSerializer


class EventSerializer(ModelSerializer):
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Event
        fields = '__all__'

    def update(self, instance, validated_data):
        request = self.context.get('request')

        if request.user != instance.organizer:
            raise ValidationError('Только организатор может изменять статус события.')

        instance.status = validated_data['status']
        instance.save(update_fields=['status'])
        return instance
