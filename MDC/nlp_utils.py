import spacy
import re

nlp = spacy.load("en_core_web_md")

def preprocess_text(text):
    # Remove any excessive whitespace
    text = re.sub(' +', ' ', text)

    # Remove newline characters
    text = text.replace('\n', ' ')

    text = text.strip()

    # Correct encoding errors
    text = text.encode('ascii', errors='ignore').decode()

    return text

def extract_text(content):
    """
    Extracts text from the given content using spaCy.
    :param content: The text content to process.
    :return: A list of sentences.
    """
    content = preprocess_text(content)  # preprocess text
    doc = nlp(content)
    sentences = [sent.text for sent in doc.sents]
    print(f"Extracted {len(sentences)} sentences from the content.")  # Add this line
    return sentences

def extract_noun_phrases(content):
    """
    Extracts noun phrases from the given content using spaCy.
    :param content: The text content to process.
    :return: A list of noun phrases.
    """
    content = preprocess_text(content)  # preprocess text
    doc = nlp(content)
    noun_phrases = [chunk.text for chunk in doc.noun_chunks]
    return noun_phrases

def extract_entities(content):
    """
    Extracts named entities from the given content using spaCy.
    :param content: The text content to process.
    :return: A dictionary with entity types as keys and a list of entities of that type as values.
    """
    content = preprocess_text(content)  # preprocess text
    doc = nlp(content)
    entities = {entity.label_: [] for entity in doc.ents}
    for entity in doc.ents:
        entities[entity.label_].append(entity.text)
    return entities