from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.authtoken.models import Token

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username', 'email')
        
        
class RegisterSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email','password')
        
    def create(self, validated_data):
        new_user = User.objects.create_user(
            username = validated_data['username'],
            email = validated_data['email'],
            password = validated_data['password']
        )
        
        return new_user
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255,required=True)
    password = serializers.CharField(required=True, write_only=True)