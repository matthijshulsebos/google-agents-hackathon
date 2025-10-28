"""
Centralized LLM-based Language Detection

This module provides accurate language detection using Gemini LLM
instead of unreliable keyword-based detection.
"""
import logging
from typing import Optional
from google import genai
from google.genai import types
from config import config

logger = logging.getLogger(__name__)

# Singleton client instance
_client: Optional[genai.Client] = None


def get_client() -> genai.Client:
    """
    Get or create Gemini client instance

    Returns:
        Configured Gemini client
    """
    global _client
    if _client is None:
        _client = genai.Client(
            vertexai=True,
            project=config.PROJECT_ID,
            location=config.LOCATION
        )
        logger.info("Initialized Gemini client for language detection")
    return _client


def detect_language_llm(text: str) -> str:
    """
    Detect the language of the input text using LLM.

    This is more accurate than keyword-based detection because the LLM
    understands context, grammar, and can handle mixed or uncommon phrases.

    Supported languages:
    - en: English
    - es: Spanish
    - fr: French
    - de: German

    Args:
        text: Text to analyze for language detection

    Returns:
        Language code (en, es, fr, de)
        Defaults to 'en' if detection fails

    Examples:
        >>> detect_language_llm("¿Cómo estás?")
        'es'
        >>> detect_language_llm("How are you?")
        'en'
        >>> detect_language_llm("Comment allez-vous?")
        'fr'
        >>> detect_language_llm("Wie geht es dir?")
        'de'
    """
    try:
        client = get_client()

        # Create a precise prompt for language detection
        detection_prompt = f"""Detect the language of the following text and respond with ONLY the language code.

Supported languages:
- en (English)
- es (Spanish)
- fr (French)
- de (German)

Text: "{text}"

Respond with ONLY ONE of these codes: en, es, fr, de
Do not include any explanation, just the code."""

        response = client.models.generate_content(
            model=config.MODEL_NAME,
            contents=detection_prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,  # Deterministic for consistent detection
                max_output_tokens=10,  # We only need 2 characters
            )
        )

        # Extract and clean the response
        detected_lang = response.text.strip().lower()

        # Validate the response
        valid_languages = {'en', 'es', 'fr', 'de'}
        if detected_lang in valid_languages:
            logger.info(f"Detected language: {detected_lang} for text: '{text[:50]}...'")
            return detected_lang
        else:
            logger.warning(f"Invalid language code '{detected_lang}' returned, defaulting to 'en'")
            return 'en'

    except Exception as e:
        logger.error(f"Error detecting language: {e}")
        logger.info("Defaulting to English due to detection error")
        return 'en'


def get_language_name(lang_code: str) -> str:
    """
    Get full language name from code

    Args:
        lang_code: Language code (en, es, fr, de)

    Returns:
        Full language name
    """
    language_names = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German'
    }
    return language_names.get(lang_code, 'English')


def get_language_instruction(lang_code: str) -> str:
    """
    Get system instruction for responding in detected language

    Args:
        lang_code: Language code (en, es, fr, de)

    Returns:
        System instruction text to ensure response matches query language
    """
    lang_name = get_language_name(lang_code)

    if lang_code == 'en':
        return f"\n\n🌐 LANGUAGE INSTRUCTION: The user's query is in {lang_name}. Respond in clear, professional {lang_name}."
    else:
        return f"\n\n🌐 CRITICAL LANGUAGE INSTRUCTION: The user's query is in {lang_name}. You MUST respond ENTIRELY in {lang_name}. Every single word, sentence, and explanation must be in {lang_name}. Use proper {lang_name} terminology throughout."
