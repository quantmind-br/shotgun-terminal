"""Settings management with XDG-compliant storage."""

import json
import os
from pathlib import Path
from typing import Dict, Any


class SettingsManager:
    """Manage application settings with XDG-compliant storage."""

    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.settings_file = self.config_dir / "settings.json"
        self.ensure_config_dir()

    def _get_config_dir(self) -> Path:
        """Get XDG-compliant config directory."""
        # Use XDG_CONFIG_HOME if set, otherwise default to ~/.config
        config_home = os.environ.get("XDG_CONFIG_HOME")
        if config_home:
            return Path(config_home) / "shotgun-code"
        else:
            return Path.home() / ".config" / "shotgun-code"

    def ensure_config_dir(self):
        """Ensure config directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file."""
        if not self.settings_file.exists():
            return self._get_default_settings()

        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                settings = json.load(f)

            # Merge with defaults to ensure all keys exist
            default_settings = self._get_default_settings()
            default_settings.update(settings)
            return default_settings

        except (json.JSONDecodeError, IOError):
            return self._get_default_settings()

    def save_settings(self, settings: Dict[str, Any]):
        """Save settings to file."""
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise Exception(f"Failed to save settings: {e}")

    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default settings."""
        return {
            "customIgnoreRules": "\n".join(
                [
                    "*.pyc",
                    "__pycache__",
                    ".git",
                    ".gitignore",
                    "*.log",
                    "node_modules",
                    ".env",
                    "*.tmp",
                    ".DS_Store",
                    "build",
                    "dist",
                    "*.egg-info",
                    ".vscode",
                    ".idea",
                ]
            ),
            "lastUsedDirectory": "",
            "defaultPromptType": "dev",
            "apiSettings": {
                "api_key": "",
                "base_url": "",
                "model": "gpt-4.1",
                "enable_translation": True,
            },
            "geminiSettings": {
                "api_key": "",
                "enable_gemini": False,
                "temperature": 0.35,
                "thinking_budget": 32768,
            },
        }

    def get_custom_ignore_rules(self) -> str:
        """Get custom ignore rules."""
        settings = self.load_settings()
        return settings.get("customIgnoreRules", "")

    def set_custom_ignore_rules(self, rules: str):
        """Set custom ignore rules."""
        settings = self.load_settings()
        settings["customIgnoreRules"] = rules
        self.save_settings(settings)

    def get_last_used_directory(self) -> str:
        """Get last used directory."""
        settings = self.load_settings()
        return settings.get("lastUsedDirectory", "")

    def set_last_used_directory(self, directory: str):
        """Set last used directory."""
        settings = self.load_settings()
        settings["lastUsedDirectory"] = directory
        self.save_settings(settings)

    def get_api_settings(self) -> Dict[str, Any]:
        """Get API settings."""
        settings = self.load_settings()
        return settings.get(
            "apiSettings",
            {
                "api_key": "",
                "base_url": "",
                "model": "gpt-4.1",
                "enable_translation": True,
            },
        )

    def set_api_settings(
        self,
        api_key: str,
        base_url: str,
        model: str = "gpt-4.1",
        enable_translation: bool = True,
    ):
        """Set API settings."""
        settings = self.load_settings()
        settings["apiSettings"] = {
            "api_key": api_key,
            "base_url": base_url,
            "model": model,
            "enable_translation": enable_translation,
        }
        self.save_settings(settings)

    def is_translation_enabled(self) -> bool:
        """Check if translation is enabled."""
        api_settings = self.get_api_settings()
        return api_settings.get("enable_translation", True)

    def set_translation_enabled(self, enabled: bool):
        """Enable or disable translation."""
        settings = self.load_settings()
        if "apiSettings" not in settings:
            settings["apiSettings"] = self._get_default_settings()["apiSettings"]
        settings["apiSettings"]["enable_translation"] = enabled
        self.save_settings(settings)

    def get_gemini_settings(self) -> Dict[str, Any]:
        """Get Gemini settings."""
        settings = self.load_settings()
        return settings.get(
            "geminiSettings",
            {
                "api_key": "",
                "enable_gemini": False,
                "temperature": 0.35,
                "thinking_budget": 32768,
            },
        )

    def set_gemini_settings(
        self,
        api_key: str,
        enable_gemini: bool = True,
        temperature: float = 0.35,
        thinking_budget: int = 32768,
    ):
        """Set Gemini settings."""
        # Validate parameters
        if not (0.0 <= temperature <= 2.0):
            raise ValueError(
                f"Temperature must be between 0.0 and 2.0, got {temperature}"
            )

        if not (0 <= thinking_budget <= 32768):
            raise ValueError(
                f"Thinking budget must be between 0 and 32768, got {thinking_budget}"
            )

        settings = self.load_settings()
        settings["geminiSettings"] = {
            "api_key": api_key,
            "enable_gemini": enable_gemini,
            "temperature": temperature,
            "thinking_budget": thinking_budget,
        }
        self.save_settings(settings)

    def is_gemini_enabled(self) -> bool:
        """Check if Gemini is enabled."""
        gemini_settings = self.get_gemini_settings()
        return gemini_settings.get("enable_gemini", False)

    def set_gemini_enabled(self, enabled: bool):
        """Enable or disable Gemini."""
        settings = self.load_settings()
        if "geminiSettings" not in settings:
            settings["geminiSettings"] = self._get_default_settings()["geminiSettings"]
        settings["geminiSettings"]["enable_gemini"] = enabled
        self.save_settings(settings)

    def get_gemini_api_key(self) -> str:
        """Get Gemini API key."""
        gemini_settings = self.get_gemini_settings()
        return gemini_settings.get("api_key", "")

    def set_gemini_api_key(self, api_key: str):
        """Set Gemini API key."""
        settings = self.load_settings()
        if "geminiSettings" not in settings:
            settings["geminiSettings"] = self._get_default_settings()["geminiSettings"]
        settings["geminiSettings"]["api_key"] = api_key
        self.save_settings(settings)

    def get_gemini_temperature(self) -> float:
        """Get Gemini temperature."""
        gemini_settings = self.get_gemini_settings()
        return gemini_settings.get("temperature", 0.35)

    def set_gemini_temperature(self, temperature: float):
        """Set Gemini temperature."""
        if not (0.0 <= temperature <= 2.0):
            raise ValueError(
                f"Temperature must be between 0.0 and 2.0, got {temperature}"
            )

        settings = self.load_settings()
        if "geminiSettings" not in settings:
            settings["geminiSettings"] = self._get_default_settings()["geminiSettings"]
        settings["geminiSettings"]["temperature"] = temperature
        self.save_settings(settings)

    def get_gemini_thinking_budget(self) -> int:
        """Get Gemini thinking budget."""
        gemini_settings = self.get_gemini_settings()
        return gemini_settings.get("thinking_budget", 32768)

    def set_gemini_thinking_budget(self, thinking_budget: int):
        """Set Gemini thinking budget."""
        if not (0 <= thinking_budget <= 32768):
            raise ValueError(
                f"Thinking budget must be between 0 and 32768, got {thinking_budget}"
            )

        settings = self.load_settings()
        if "geminiSettings" not in settings:
            settings["geminiSettings"] = self._get_default_settings()["geminiSettings"]
        settings["geminiSettings"]["thinking_budget"] = thinking_budget
        self.save_settings(settings)
