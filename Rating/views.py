from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Movies, Critics
import requests
from django.core.mail import send_mail
from django.conf import settings

## Define serializer
## Define serializer
class CriticSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    movie_name = serializers.CharField(max_length=100)
    criticText = serializers.CharField(max_length=500)
    criticRating = serializers.IntegerField(default=1)

    class Meta:
        model = Critics
        fields = ['username', 'movie_name', 'criticText', 'criticRating']

    def validate_movie_name(self, movie_name):
        """
        Validate the movie name by checking if it's in the database.
        If not, fetch it from the external API and add it to the database.
        """
        # Normalize the movie name (lowercase and strip spaces)
        normalized_movie_name = movie_name.strip().lower()

        try:
            # Normalize the movie names in the database for comparison
            movie = Movies.objects.get(movieName__iexact=normalized_movie_name)
        except Movies.DoesNotExist:
            formatted_movie_name = movie_name.replace(' ', '+')

            api_key = 'f84fc31d'
            external_api_url = f'http://www.omdbapi.com/?apikey={api_key}&t={formatted_movie_name}'
            response = requests.get(external_api_url)

            if response.status_code == 200:
                movie_data = response.json()
                if movie_data.get('Response') == 'True':
                    # Normalize the title from the API before saving
                    movie = Movies.objects.create(
                        movieName=movie_data['Title'].strip().lower()  # Normalize movie name
                    )
                else:
                    raise serializers.ValidationError("Movie not found in external API.")
            else:
                raise serializers.ValidationError("Failed to fetch movie from external API.")

        return movie

    def create(self, validated_data):
        movie = validated_data.pop('movie_name')
        user = validated_data['user']

        # Check if this user has already rated this movie
        critic = Critics.objects.filter(user=user, movieName=movie).first()

        if critic:
            critic.criticText = validated_data.get('criticText', critic.criticText)
            critic.criticRating = validated_data.get('criticRating', critic.criticRating)
            critic.save()
        else:
            critic = Critics.objects.create(movieName=movie, **validated_data)
            # notify all other users who have written a critic for this movie
            self.notify_users(movie, user)


        return critic

    def notify_users(self, movie, current_user):
        """
        Notify all users who have previously written a critic for the movie,
        except the current user who added the new critic.
        """
        previous_critics = Critics.objects.filter(movieName=movie).exclude(user=current_user)

        if previous_critics.exists():
            recipient_emails = [critic.user.email for critic in previous_critics]
            print(recipient_emails)
            if recipient_emails:
                send_mail(
                    subject=f"New Critic Added for {movie.movieName}",
                    message=f"A new critic has been added for the movie '{movie.movieName}' by '{current_user}'. Check it out!",
                    from_email=settings.DEFAULT_FROM_EMAIL,  
                    recipient_list=recipient_emails,
                    fail_silently=False,
                )

class CriticView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CriticSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message": "Critic added successfully"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)