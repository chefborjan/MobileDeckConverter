from django.db import models
import os

def get_deck_upload_path(instance, filename):
    return os.path.join(f'uploads/{instance.id}/', filename)

def get_image_upload_path(instance, filename):
    return os.path.join(f'uploads/{instance.deck.id}/images/', filename)


class PitchDeck(models.Model):
    original_deck = models.FileField(upload_to=get_deck_upload_path)
    mobile_friendly_deck = models.FileField(upload_to='mobile_decks/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    extracted_text = models.TextField(null=True, blank=True)
    noun_phrases = models.JSONField(null=True, blank=True)
    named_entities = models.JSONField(null=True, blank=True)
    number_of_pages = models.IntegerField(default=0)    # added this line
    number_of_images = models.IntegerField(default=0)  # added this line

    def __str__(self):
        return f"Pitch Deck {self.id}"

class DeckImage(models.Model):
    deck = models.ForeignKey(PitchDeck, related_name='deck_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_image_upload_path)
