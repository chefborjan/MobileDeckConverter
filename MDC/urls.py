from django.urls import path
from . import views  # Import the views module from the current package

urlpatterns = [
    # Map the URL /upload/ to the upload_deck view
    path('upload/', views.upload_deck, name='upload_deck'),
    # Map the URL /decks/<deck_id>/ to the view_deck view
    path('decks/<int:deck_id>/', views.view_deck, name='view_deck'),
]