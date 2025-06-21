"""Configuration management for API settings."""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
import inquirer

from .settings import SettingsManager
from .translator import TranslationService

console = Console()

class ConfigManager:
    """Manage API configuration settings."""
    
    def __init__(self):
        self.settings = SettingsManager()
        self.translator = TranslationService()
    
    def configure_api(self):
        """Interactive API configuration."""
        console.print(Panel.fit(
            "[bold cyan]🔧 API Configuration[/bold cyan]\n"
            "Configure OpenAI-compatible API for translation",
            border_style="cyan"
        ))
        
        # Show current settings
        self._show_current_settings()
        
        # Configuration menu
        while True:
            action = inquirer.list_input(
                "Choose configuration action",
                choices=[
                    'Configure API credentials',
                    'Test API connection',
                    'Toggle translation on/off',
                    'View current settings',
                    'Reset to defaults',
                    'Exit configuration'
                ]
            )
            
            if action == 'Configure API credentials':
                self._configure_credentials()
            elif action == 'Test API connection':
                self._test_connection()
            elif action == 'Toggle translation on/off':
                self._toggle_translation()
            elif action == 'View current settings':
                self._show_current_settings()
            elif action == 'Reset to defaults':
                self._reset_to_defaults()
            elif action == 'Exit configuration':
                break
    
    def _configure_credentials(self):
        """Configure API credentials."""
        console.print("\n[yellow]Configure API Credentials[/yellow]")
        
        current_settings = self.settings.get_api_settings()
        
        # API Key
        current_key = current_settings.get('api_key', '')
        masked_key = f"{current_key[:8]}...{current_key[-4:]}" if len(current_key) > 12 else "Not set"
        console.print(f"[blue]Current API Key:[/blue] {masked_key}")
        
        new_key = Prompt.ask("Enter API Key", default=current_key if current_key else "")
        
        # Base URL
        current_url = current_settings.get('base_url', '')
        console.print(f"[blue]Current Base URL:[/blue] {current_url or 'Not set'}")
        
        new_url = Prompt.ask("Enter Base URL", default=current_url if current_url else "https://copilot.quantmind.com.br")
        
        # Model
        current_model = current_settings.get('model', 'gpt-4.1')
        console.print(f"[blue]Current Model:[/blue] {current_model}")
        
        new_model = Prompt.ask("Enter Model", default=current_model)
        
        # Enable translation
        current_enabled = current_settings.get('enable_translation', True)
        enable_translation = Confirm.ask("Enable translation?", default=current_enabled)
        
        # Save settings
        if new_key and new_url:
            self.settings.set_api_settings(new_key, new_url, new_model, enable_translation)
            console.print("[green]✓[/green] API settings saved successfully!")
            
            # Reinitialize translator with new settings
            self.translator._initialize_client()
            
            # Test connection
            if Confirm.ask("Test connection now?", default=True):
                self._test_connection()
        else:
            console.print("[red]Error:[/red] API Key and Base URL are required")
    
    def _test_connection(self):
        """Test API connection."""
        console.print("\n[yellow]Testing API Connection[/yellow]")
        
        if not self.translator.is_configured():
            console.print("[red]Error:[/red] API not configured. Please configure credentials first.")
            return
        
        if self.translator.test_connection():
            console.print("[green]✓[/green] API connection successful!")
            
            # Test translation
            if Confirm.ask("Test translation functionality?", default=True):
                test_text = "Olá, este é um teste de tradução."
                console.print(f"[blue]Testing translation:[/blue] {test_text}")
                
                translated = self.translator.translate_to_english(test_text, "test")
                if translated:
                    console.print(f"[green]✓[/green] Translation result: {translated}")
                else:
                    console.print("[red]✗[/red] Translation failed")
        else:
            console.print("[red]✗[/red] API connection failed!")
    
    def _toggle_translation(self):
        """Toggle translation on/off."""
        current_enabled = self.settings.is_translation_enabled()
        new_enabled = not current_enabled
        
        self.settings.set_translation_enabled(new_enabled)
        
        status = "enabled" if new_enabled else "disabled"
        console.print(f"[green]✓[/green] Translation {status}")
    
    def _show_current_settings(self):
        """Show current API settings."""
        console.print("\n[blue]Current API Settings:[/blue]")
        
        settings = self.settings.get_api_settings()
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Setting", style="dim", width=20)
        table.add_column("Value")
        
        # Mask API key for security
        api_key = settings.get('api_key', '')
        masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "Not configured"
        
        table.add_row("API Key", masked_key)
        table.add_row("Base URL", settings.get('base_url', 'Not configured'))
        table.add_row("Model", settings.get('model', 'gpt-4.1'))
        table.add_row("Translation Enabled", "Yes" if settings.get('enable_translation', True) else "No")
        table.add_row("Status", "Configured" if self.translator.is_configured() else "Not configured")
        
        console.print(table)
        console.print()
    
    def _reset_to_defaults(self):
        """Reset API settings to defaults."""
        if Confirm.ask("Reset all API settings to defaults? This will remove your credentials.", default=False):
            default_api_settings = self.settings._get_default_settings()["apiSettings"]
            self.settings.set_api_settings(
                default_api_settings["api_key"],
                default_api_settings["base_url"],
                default_api_settings["model"],
                default_api_settings["enable_translation"]
            )
            console.print("[green]✓[/green] Settings reset to defaults")
            
            # Reinitialize translator
            self.translator._initialize_client()
    
    def quick_setup(self):
        """Quick setup with provided test credentials."""
        console.print(Panel.fit(
            "[bold green]🚀 Quick Setup[/bold green]\n"
            "Setting up with test credentials",
            border_style="green"
        ))
        
        # Set up with provided test credentials
        test_api_key = "ck_4c5a9f054475f54d91a17e5e5a0b545c"
        test_base_url = "https://copilot.quantmind.com.br"
        test_model = "gpt-4.1"
        
        self.settings.set_api_settings(test_api_key, test_base_url, test_model, True)
        console.print("[green]✓[/green] Test credentials configured!")
        
        # Reinitialize translator
        self.translator._initialize_client()
        
        # Test connection
        console.print("\n[blue]Testing connection...[/blue]")
        if self.translator.test_connection():
            console.print("[green]✓[/green] Quick setup completed successfully!")
        else:
            console.print("[red]✗[/red] Connection test failed. Please check credentials.")