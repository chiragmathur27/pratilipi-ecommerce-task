from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
    def get(self, request, user_id=None):
        if user_id:
            product = get_object_or_404(self.get_queryset(), id=user_id)  # Simplified using get_object_or_404
            serializer = RegisterSerializer(product)
            return Response(serializer.data)
        else:
            products = self.get_queryset()
            serializer = RegisterSerializer(products, many=True)
            return Response(serializer.data)
    
    def put(self, request, user_id):
        try:
            user = get_object_or_404(User, id=user_id)
            
            # Ensure users can only update their own data
            if request.user.id != user.id:
                return Response(
                    {"error": "You can only update your own data"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = RegisterSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UpdateUserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save user updates
            user.emit_user_updated_event()  # Emit user updated event
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = User.objects.get(email=email)
            if check_password(password, user.password):
                refresh = RefreshToken.for_user(user)
                user_serializer = UserSerializer(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': user_serializer.data
                })
            else:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        

class DashboardView(APIView):
    permission_classes = (IsAuthenticated, )
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response({'message':'Welcome to dashboard!','user':serializer.data},200)