from django.shortcuts import render, redirect, get_object_or_404
from .models import PitchDeck, DeckImage
from .nlp_utils import extract_text, extract_noun_phrases, extract_entities
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
import json
import fitz
import os
import logging
from django.core.files import File
from django.contrib import messages
from django.conf import settings
from PIL import Image
import io

# Configure the logger
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

logging.error("Test log message")  # Add this line


def upload_deck(request):
    if request.method == 'POST':
        if 'deck' not in request.FILES:
            messages.error(request, 'Please upload a deck.')
            return redirect('upload_deck')

        new_deck = PitchDeck()
        new_deck.save()  # This will generate an id for the new_deck instance
        new_deck.original_deck = request.FILES['deck']  # Now the id is available for get_deck_upload_path
        new_deck.save()

        # Initialize PyMuPDF Document
        doc = fitz.open(new_deck.original_deck.path)

        # set number_of_pages
        new_deck.number_of_pages = len(doc)

        extracted_text_per_page = []
        noun_phrases_per_page = []
        named_entities_per_page = []
        number_of_images = 0  # Initialize variable to count images

        print(f"Document has {new_deck.number_of_pages} pages.")  # Updated this print

        for i in range(len(doc)):
            print(f"Before try block for page {i + 1}.")  # Add this print
            try:
                print(f"Processing page {i + 1}/{len(doc)}")  # Keep this print
                page = doc[i]
                page_text = page.get_text()
                if page_text.strip() == '':
                    print(f"Page {i + 1} doesn't contain any extractable text.")  # Keep this print
                    continue
                print(f"Page {i + 1} text: {page_text[:100]}...")  # Keep this print

                extracted_text = extract_text(page_text)
                noun_phrases = extract_noun_phrases(page_text)
                named_entities = extract_entities(page_text)

                extracted_text_per_page.append(extracted_text)
                noun_phrases_per_page.append(noun_phrases)
                named_entities_per_page.append(named_entities)

                print(f"Text, phrases, and entities extracted for page {i + 1}.")  # Keep this print

                # Extract images
                # Update the count of images
                number_of_images += len(page.get_images())

                print(f"Found {len(page.get_images())} image(s) on page {i + 1}.")
                for idx, img in enumerate(page.get_images()):  # Added enumerate to get an index
                    xref = img[0]
                    base = img[1]
                    pix = fitz.Pixmap(doc, xref)
                    if pix.n < 5:  # this is GRAY or RGB
                        pil_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    else:  # CMYK: convert to RGB first
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                        pil_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                    # Save the PIL Image object to an in-memory file
                    img_io = io.BytesIO()
                    pil_img.save(img_io, format='PNG')
                    img_io.seek(0)

                    # Create a new DeckImage instance and associate it with the PitchDeck
                    deck_image = DeckImage()
                    # Associate the image with the deck BEFORE saving the model
                    deck_image.deck = new_deck
                    # Use idx in the filename
                    deck_image.image.save(f"page{i + 1}-{idx}-{base}.png", File(img_io), save=True)
                    deck_image.save()

                    logging.error(f'Saved image {deck_image.id} for deck {new_deck.id}')  # Add this line

            except Exception as e:
                logging.error(f"Error processing page {i + 1}: {e}", exc_info=True)
                continue

            print(f"After try block for page {i + 1}.")  # Add this print

        # Set number of images for the deck
        new_deck.number_of_images = number_of_images

        # after the for loop where you extract the text, noun phrases, and entities
        with open(os.path.join(settings.MEDIA_ROOT, f'uploads/{new_deck.id}/extracted_text.txt'), 'w') as f:
            for idx, page_text in enumerate(extracted_text_per_page):
                f.write(f'Page {idx + 1}:\n{page_text}\n\n')

        with open(os.path.join(settings.MEDIA_ROOT, f'uploads/{new_deck.id}/noun_phrases.txt'), 'w') as f:
            for idx, page_phrases in enumerate(noun_phrases_per_page):
                f.write(f'Page {idx + 1}:\n{page_phrases}\n\n')

        with open(os.path.join(settings.MEDIA_ROOT, f'uploads/{new_deck.id}/named_entities.txt'), 'w') as f:
            for idx, page_entities in enumerate(named_entities_per_page):
                f.write(f'Page {idx + 1}:\n{page_entities}\n\n')

        new_deck.extracted_text = json.dumps(extracted_text_per_page)
        new_deck.noun_phrases = json.dumps(noun_phrases_per_page)
        new_deck.named_entities = json.dumps(named_entities_per_page)

        new_deck.save()

        print("Deck saved.")  # Keep this print

        return redirect('view_deck', deck_id=new_deck.id)

    return render(request, 'upload_deck.html')


def view_deck(request, deck_id):
    new_deck = get_object_or_404(PitchDeck, id=deck_id)

    try:
        mobile_friendly_deck_url = new_deck.mobile_friendly_deck.url
    except ValueError:
        mobile_friendly_deck_url = None

    context = {
        'deck': new_deck,
        'mobile_friendly_deck_url': mobile_friendly_deck_url,
        'extracted_text': json.loads(new_deck.extracted_text),  # use the deserialized versions
        'noun_phrases': json.loads(new_deck.noun_phrases),
        'named_entities': json.loads(new_deck.named_entities),
        'number_of_pages': new_deck.number_of_pages,  # Added this line
        'number_of_images': new_deck.number_of_images  # Added this line
    }

    return render(request, 'view_deck.html', context)
