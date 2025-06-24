"""Configuration management for API settings."""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
import inquirer

from .settings import SettingsManager
from .translator import TranslationService
from .gemini_service import GeminiService

console = Console()

class ConfigManager:
    """Manage API configuration settings."""
    
    def __init__(self):
        self.settings = SettingsManager()
        self.translator = TranslationService()
        self.gemini_service = GeminiService()
    
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
    
    def configure_gemini(self):
        """Interactive Gemini configuration."""
        console.print(Panel.fit(
            "[bold cyan]🤖 Gemini API Configuration[/bold cyan]\n"
            "Configure Google Gemini API for automated prompt processing",
            border_style="cyan"
        ))
        
        # Show current Gemini settings
        self._show_current_gemini_settings()
        
        # Configuration menu
        while True:
            action = inquirer.list_input(
                "Choose Gemini configuration action",
                choices=[
                    'Configure Gemini API credentials',
                    'Test Gemini API connection',
                    'Configure parameters (temperature, thinking budget)',
                    'Toggle Gemini on/off',
                    'View current Gemini settings',
                    'Reset Gemini to defaults',
                    'Exit Gemini configuration'
                ]
            )
            
            if action == 'Configure Gemini API credentials':
                self._configure_gemini_credentials()
            elif action == 'Test Gemini API connection':
                self._test_gemini_connection()
            elif action == 'Configure parameters (temperature, thinking budget)':
                self._configure_gemini_parameters()
            elif action == 'Toggle Gemini on/off':
                self._toggle_gemini()
            elif action == 'View current Gemini settings':
                self._show_current_gemini_settings()
            elif action == 'Reset Gemini to defaults':
                self._reset_gemini_to_defaults()
            elif action == 'Exit Gemini configuration':
                break
    
    def _configure_gemini_credentials(self):
        """Configure Gemini API credentials."""
        console.print("\n[yellow]Configure Gemini API Credentials[/yellow]")
        
        current_settings = self.settings.get_gemini_settings()
        
        # API Key
        current_key = current_settings.get('api_key', '')
        masked_key = f"{current_key[:8]}...{current_key[-4:]}" if len(current_key) > 12 else "Not set"
        console.print(f"[blue]Current Gemini API Key:[/blue] {masked_key}")
        
        new_key = Prompt.ask("Enter Gemini API Key", default=current_key if current_key else "")
        
        if new_key:
            # Configure the service
            if self.gemini_service.configure(new_key):
                # Save to settings
                current_settings['api_key'] = new_key
                self.settings.set_gemini_settings(
                    api_key=new_key,
                    enable_gemini=current_settings.get('enable_gemini', False),
                    temperature=current_settings.get('temperature', 0.35),
                    thinking_budget=current_settings.get('thinking_budget', 32768)
                )
                console.print("[green]✓[/green] Gemini API key saved successfully!")
                
                # Test connection
                if Confirm.ask("Test Gemini connection now?", default=True):
                    self._test_gemini_connection()
            else:
                console.print("[red]Error:[/red] Failed to configure Gemini API")
        else:
            console.print("[red]Error:[/red] API Key is required")
    
    def _test_gemini_connection(self):
        """Test Gemini API connection."""
        console.print("\n[yellow]Testing Gemini API Connection[/yellow]")
        
        api_key = self.settings.get_gemini_api_key()
        if not api_key:
            console.print("[red]Error:[/red] Gemini API not configured. Please configure credentials first.")
            return
        
        # Configure and test
        if self.gemini_service.configure(api_key):
            if self.gemini_service.test_connection():
                console.print("[green]✓[/green] Gemini API connection successful!")
            else:
                console.print("[red]✗[/red] Gemini API connection failed!")
        else:
            console.print("[red]✗[/red] Failed to configure Gemini API!")
    
    def _configure_gemini_parameters(self):
        """Configure Gemini parameters."""
        console.print("\n[yellow]Configure Gemini Parameters[/yellow]")
        
        current_settings = self.settings.get_gemini_settings()
        
        # Temperature
        current_temp = current_settings.get('temperature', 0.35)
        console.print(f"[blue]Current Temperature:[/blue] {current_temp} (range: 0.0 - 2.0)")
        
        while True:
            try:
                new_temp_str = Prompt.ask(f"Enter Temperature", default=str(current_temp))
                new_temp = float(new_temp_str)
                if 0.0 <= new_temp <= 2.0:
                    break
                else:
                    console.print("[red]Error:[/red] Temperature must be between 0.0 and 2.0")
            except ValueError:
                console.print("[red]Error:[/red] Please enter a valid number")
        
        # Thinking Budget
        current_budget = current_settings.get('thinking_budget', 32768)
        console.print(f"[blue]Current Thinking Budget:[/blue] {current_budget} (range: 0 - 32768)")
        
        while True:
            try:
                new_budget_str = Prompt.ask(f"Enter Thinking Budget", default=str(current_budget))
                new_budget = int(new_budget_str)
                if 0 <= new_budget <= 32768:
                    break
                else:
                    console.print("[red]Error:[/red] Thinking budget must be between 0 and 32768")
            except ValueError:
                console.print("[red]Error:[/red] Please enter a valid integer")
        
        # Save settings
        try:
            self.settings.set_gemini_settings(
                api_key=current_settings.get('api_key', ''),
                enable_gemini=current_settings.get('enable_gemini', False),
                temperature=new_temp,
                thinking_budget=new_budget
            )
            console.print("[green]✓[/green] Gemini parameters saved successfully!")
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
    
    def _toggle_gemini(self):
        """Toggle Gemini on/off."""
        current_enabled = self.settings.is_gemini_enabled()
        new_enabled = not current_enabled
        
        self.settings.set_gemini_enabled(new_enabled)
        
        status = "enabled" if new_enabled else "disabled"
        console.print(f"[green]✓[/green] Gemini {status}")
        
        if new_enabled:
            api_key = self.settings.get_gemini_api_key()
            if not api_key:
                console.print("[yellow]Warning:[/yellow] Gemini is enabled but no API key is configured")
                if Confirm.ask("Configure API key now?", default=True):
                    self._configure_gemini_credentials()
    
    def _show_current_gemini_settings(self):
        """Show current Gemini settings."""
        console.print("\n[blue]Current Gemini Settings:[/blue]")
        
        settings = self.settings.get_gemini_settings()
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Setting", style="dim", width=20)
        table.add_column("Value")
        
        # Mask API key for security
        api_key = settings.get('api_key', '')
        masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "Not configured"
        
        table.add_row("API Key", masked_key)
        table.add_row("Gemini Enabled", "Yes" if settings.get('enable_gemini', False) else "No")
        table.add_row("Temperature", str(settings.get('temperature', 0.35)))
        table.add_row("Thinking Budget", str(settings.get('thinking_budget', 32768)))
        table.add_row("Status", "Configured" if api_key else "Not configured")
        
        console.print(table)
        console.print()
    
    def _reset_gemini_to_defaults(self):
        """Reset Gemini settings to defaults."""
        if Confirm.ask("Reset all Gemini settings to defaults? This will remove your API key.", default=False):
            default_gemini_settings = self.settings._get_default_settings()["geminiSettings"]
            self.settings.set_gemini_settings(
                default_gemini_settings["api_key"],
                default_gemini_settings["enable_gemini"],
                default_gemini_settings["temperature"],
                default_gemini_settings["thinking_budget"]
            )
            console.print("[green]✓[/green] Gemini settings reset to defaults")