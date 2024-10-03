# from rest_framework import serializers
# from rest_framework.serializers import ModelSerializer
# from .models import User  # Import the custom User model

# class UserSerializer(ModelSerializer):
#     class Meta:
#         model = User  # Use the custom User model
#         fields = ('id','username', 'email')
        
        
# class RegisterSerializer(ModelSerializer):
#     class Meta:
#         model = User  # Use the custom User model
#         fields = ('username', 'email','password')
        
#     def create(self, validated_data):
#         new_user = User.objects.create_user(
#             username = validated_data['username'],
#             email = validated_data['email'],
#             password = validated_data['password']
#         )
        
#         return new_user
    
# class LoginSerializer(serializers.Serializer):
#     email = serializers.EmailField(max_length=255,required=True)
#     password = serializers.CharField(required=True, write_only=True)

# users/serializers.py
from rest_framework import serializers
from .models import User
from users.producer import send_user_created_event

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        # Create the user
        user = User.objects.create_user(**validated_data)  # Call the create_user method

        # Emit user created event
        send_user_created_event(user.id, user.username, user.email)

        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, required=True)
    password = serializers.CharField(required=True, write_only=True)
