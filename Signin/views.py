from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
import re

# Serializer
class SigninSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=50, write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    email = serializers.EmailField(max_length=100)

    # Password match validation
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        # Check if the username and email are unique in the User model
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "This username is already taken."})

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "This email is already registered."})

        ## IMPORTANT!
        #Password validation is commented for the sake of easy testing

        # # Validate password length (at least 8 characters)
        # if len(data['password']) < 8:
        #     raise serializers.ValidationError({"password": "Password must be at least 8 characters long."})
        #
        # # Validate password for at least one capital letter
        # if not re.search(r'[A-Z]', data['password']):
        #     raise serializers.ValidationError({"password": "Password must contain at least one capital letter."})
        #
        # # Validate password for at least one number
        # if not re.search(r'[0-9]', data['password']):
        #     raise serializers.ValidationError({"password": "Password must contain at least one number."})

        return data

    # Create a user after validation
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        validated_data['password'] = make_password(validated_data['password'])
        return User.objects.create(**validated_data)



# Signin API
class SigninView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SigninSerializer(data=request.data)

        # Data validation check
        if serializer.is_valid():
            # Save the new user
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)

        # Return errors if validation fails
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Login API
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)
            if check_password(password, user.password):
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    'token': token.key,
                    'user_id': user.pk,
                    'email': user.email
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
