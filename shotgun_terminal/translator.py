"""Translation service using OpenAI-compatible API."""

import openai
from typing import Optional
from rich.console import Console

from .settings import SettingsManager

console = Console()


class TranslationService:
    """Handle translation using OpenAI-compatible API."""

    def __init__(self):
        self.settings = SettingsManager()
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize OpenAI client with saved settings."""
        api_settings = self.settings.get_api_settings()

        api_key = api_settings.get("api_key", "").strip()
        base_url = api_settings.get("base_url", "").strip()

        if api_key and base_url:
            try:
                self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
                console.print(
                    f"[dim]Translation API initialized with base URL: {base_url}[/dim]"
                )
            except Exception as e:
                console.print(
                    f"[yellow]Warning: Failed to initialize API client: {e}[/yellow]"
                )
                self.client = None
        else:
            console.print(
                f"[dim]Translation API not configured (api_key: {'✓' if api_key else '✗'}, base_url: {'✓' if base_url else '✗'})[/dim]"
            )
            self.client = None

    def is_configured(self) -> bool:
        """Check if API is properly configured."""
        return self.client is not None

    def translate_to_english(
        self, text: str, text_type: str = "text", force: bool = False
    ) -> Optional[str]:
        """
        Translate text to English using the configured API.

        Args:
            text: Text to translate
            text_type: Type of text ("task" or "rules" for context)
            force: Skip language detection and force translation

        Returns:
            Translated text or None if translation fails
        """
        if not self.is_configured():
            console.print(
                "[yellow]API not configured. Use 'shotgun-terminal --config' to set up translation.[/yellow]"
            )
            return None

        if not text.strip():
            return text

        # Check if text is already in English (simple heuristic) unless forced
        if not force:
            is_english = self._is_likely_english(text)
            console.print(
                f"[dim]Language detection for {text_type}: {'English' if is_english else 'Portuguese'}[/dim]"
            )

            if is_english:
                console.print(
                    "[blue]Text appears to be in English already, skipping translation[/blue]"
                )
                return text
        else:
            console.print(
                f"[yellow]Forcing translation for {text_type} (language detection bypassed)[/yellow]"
            )

        try:
            # Get model from settings
            api_settings = self.settings.get_api_settings()
            model = api_settings.get("model", "gpt-4.1")

            # Create appropriate prompt based on text type
            if text_type == "task":
                system_prompt = """You are a professional translator. Translate the following task description to English.
Keep the meaning precise and technical terms accurate. Return only the translated text without any additional commentary."""
            elif text_type == "rules":
                system_prompt = """You are a professional translator. Translate the following coding rules/guidelines to English.
Keep technical terms accurate and maintain the list format. Return only the translated text without any additional commentary."""
            else:
                system_prompt = """You are a professional translator. Translate the following text to English.
Return only the translated text without any additional commentary."""

            console.print(f"[blue]Translating {text_type} to English...[/blue]")

            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                temperature=0.1,  # Low temperature for consistent translation
                max_tokens=2000,
            )

            translated_text = response.choices[0].message.content.strip()
            console.print("[green]✓[/green] Translation completed")

            return translated_text

        except Exception as e:
            console.print(f"[red]Translation failed:[/red] {e}")
            console.print("[yellow]Using original text in Portuguese[/yellow]")
            return None

    def _is_likely_english(self, text: str) -> bool:
        """
        Simple heuristic to check if text is likely already in English.

        This is a basic check - looks for common Portuguese words/patterns.
        """
        # Strong Portuguese indicators (unique patterns)
        strong_portuguese_indicators = ["ção", "ções", "ão", "ões", "nh", "lh", "ç"]

        # Common Portuguese words
        portuguese_words = [
            "que",
            "para",
            "com",
            "uma",
            "não",
            "são",
            "está",
            "foi",
            "ser",
            "ter",
            "fazer",
            "implementar",
            "criar",
            "adicionar",
            "corrigir",
            "quando",
            "onde",
            "função",
            "método",
            "classe",
            "arquivo",
            "código",
            "aplicação",
            "sistema",
            "usuário",
            "dados",
            "página",
            "botão",
            "erro",
            "problema",
        ]

        text_lower = text.lower()

        # Check for strong Portuguese patterns first
        strong_count = sum(
            1 for indicator in strong_portuguese_indicators if indicator in text_lower
        )
        if strong_count > 0:
            return False  # Definitely Portuguese

        # Check for Portuguese words
        word_count = sum(
            1
            for word in portuguese_words
            if (f" {word} " in f" {text_lower} " or
                text_lower.startswith(f"{word} ") or
                text_lower.endswith(f" {word}"))
        )

        # If we find Portuguese words, assume it's Portuguese
        # More permissive: only require 1 clear Portuguese word
        return word_count == 0

    def test_connection(self) -> bool:
        """Test API connection and configuration."""
        if not self.is_configured():
            return False

        try:
            console.print("[blue]Testing API connection...[/blue]")

            # Get model from settings
            api_settings = self.settings.get_api_settings()
            model = api_settings.get("model", "gpt-4.1")

            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": "Hello, this is a test. Please respond with 'Test successful'.",
                    }
                ],
                max_tokens=10,
            )

            result = response.choices[0].message.content.strip()
            console.print(f"[green]✓[/green] API test successful: {result}")
            return True

        except Exception as e:
            console.print(f"[red]API test failed:[/red] {e}")
            return False
