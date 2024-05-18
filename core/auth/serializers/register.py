from rest_framework import serializers
from core.wqmsapi.serializers import UserSerializer
from core.wqmsapi.models import CustomUser

class RegisterSerializer(UserSerializer):
    #password validation
    password = serializers.CharField(max_length=126,
                                     min_length=8, write_only=True, required=True)
    

    class Meta:
        model = CustomUser
        fields = ['id', 'email','username','first_name','last_name','password']

    # def create(self, validated_data):
    #     return CustomUser.objects.create_user(**validated_data)
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user