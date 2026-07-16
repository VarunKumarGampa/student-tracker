from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, UserProfileSerializer
from .models import User


class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    Creates a new user account. No authentication required.
    Returns the user profile on success.
    """
    queryset            = User.objects.all()
    serializer_class    = RegisterSerializer
    permission_classes  = [AllowAny]   # anyone can register

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Return the created user profile
        profile = UserProfileSerializer(user)
        return Response(profile.data, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    """
    POST /api/auth/login/
    Takes email + password, returns access and refresh JWT tokens.
    Built into simplejwt — we just expose it at our URL.
    """
    permission_classes = [AllowAny]


class ProfileView(generics.RetrieveAPIView):
    """
    GET /api/auth/me/
    Returns the currently authenticated user's profile.
    Requires a valid JWT token in the Authorization header.
    """
    serializer_class   = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Returns the user making the request — not any user by ID
        return self.request.user