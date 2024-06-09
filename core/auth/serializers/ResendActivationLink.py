from rest_framework import serializers


class ResendActivationLinkSerializer(serializers.Serializer):
    email = serializers.EmailField()