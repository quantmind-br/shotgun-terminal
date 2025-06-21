"""User input collection module."""

import tempfile
import subprocess
import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
import inquirer

from .settings import SettingsManager

console = Console()

class UserInputCollector:
    """Collect user task and custom rules input."""
    
    def __init__(self):
        self.settings = SettingsManager()
    
    def collect_user_task(self) -> str:
        """Collect user task description."""
        console.print(Panel.fit(
            "[bold yellow]📝 Task Description[/bold yellow]\n"
            "Describe what you want to achieve with this project",
            border_style="yellow"
        ))
        
        # Task input
        console.print("\n[yellow]Enter your task description:[/yellow]")
        console.print("[dim]You can describe what you want to do, what needs to be fixed, or what feature to implement[/dim]")
        console.print("[dim]Type 'END' on a new line to finish[/dim]")
        
        task = self._get_multiline_terminal_input("Task description")
        
        if not task.strip():
            console.print("[red]Task description cannot be empty[/red]")
            return self.collect_user_task()
        
        # Task collected successfully
        
        return task
    
    def collect_custom_rules(self) -> str:
        """Collect custom prompt rules."""
        console.print(Panel.fit(
            "[bold cyan]⚙️ Custom Rules[/bold cyan]\n"
            "Define specific rules and guidelines for the AI to follow",
            border_style="cyan"
        ))
        
        # Ask if user wants to add custom rules
        add_rules = Confirm.ask("Add custom rules for this session?", default=False)
        
        if not add_rules:
            return ""
        
        # Get custom rules with multiline input
        console.print("\n[yellow]Enter your custom rules:[/yellow]")
        console.print("[dim]Each line will be a rule. Type 'END' on a new line to finish[/dim]")
        
        rules_input = self._get_multiline_terminal_input("Custom rules")
        
        if not rules_input.strip():
            console.print("[yellow]No rules entered[/yellow]")
            return ""
        
        # Process rules - split by lines and format
        custom_rules = []
        for line in rules_input.split('\n'):
            line = line.strip()
            if line:  # Skip empty lines
                # Add rule with proper formatting
                if not line.startswith('-'):
                    line = f"- {line}"
                custom_rules.append(line)
        
        if not custom_rules:
            console.print("[yellow]No valid rules found[/yellow]")
            return ""
        
        final_rules = '\n'.join(custom_rules)
        
        # Show preview
        console.print(f"\n[blue]Preview of your custom rules:[/blue]")
        for rule in custom_rules:
            console.print(f"  {rule}")
        
        confirm = Confirm.ask(f"\nUse these {len(custom_rules)} custom rules?", default=True)
        
        if confirm:
            console.print("[green]Custom rules will be used for this session![/green]")
            return final_rules
        else:
            console.print("[yellow]No custom rules will be used[/yellow]")
            return ""
    
    
    def _get_multiline_terminal_input(self, prompt_text: str) -> str:
        """Get multiline input directly in terminal."""
        lines = []
        console.print(f"\n[cyan]{prompt_text}:[/cyan]")
        console.print("[dim]Type your content. Type 'END' on a new line to finish[/dim]")
        
        while True:
            try:
                line = input("> ")
                
                # Check if user typed END to finish
                if line.strip().upper() == "END":
                    break
                    
                lines.append(line)
                
            except KeyboardInterrupt:
                console.print("\n[red]Input cancelled[/red]")
                return ""
            except EOFError:
                # Handle EOF gracefully (fallback)
                break
        
        return '\n'.join(lines).strip()
    
    
    def _get_multiline_input(self) -> str:
        """Get multiline input using external editor."""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as tf:
                tf.write("# Enter your task description here\n")
                tf.write("# Lines starting with # will be ignored\n\n")
                temp_path = tf.name
            
            # Open in editor
            editor = os.environ.get('EDITOR', 'notepad' if os.name == 'nt' else 'nano')
            subprocess.run([editor, temp_path], check=True)
            
            # Read content
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Clean up
            os.unlink(temp_path)
            
            # Filter out comments
            lines = [line for line in content.split('\n') if not line.strip().startswith('#')]
            return '\n'.join(lines).strip()
            
        except Exception as e:
            console.print(f"[red]Error using editor:[/red] {e}")
            console.print("[yellow]Falling back to simple input[/yellow]")
            return Prompt.ask("Task description")
    
    def _edit_rules_in_editor(self, current_rules: str) -> str:
        """Edit rules in external editor."""
        try:
            # Create temporary file with current rules
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as tf:
                tf.write("# Custom Prompt Rules\n")
                tf.write("# Each line should be a rule (- prefix optional)\n")
                tf.write("# Lines starting with # will be ignored\n\n")
                tf.write(current_rules)
                temp_path = tf.name
            
            # Open in editor
            editor = os.environ.get('EDITOR', 'notepad' if os.name == 'nt' else 'nano')
            subprocess.run([editor, temp_path], check=True)
            
            # Read content
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Clean up
            os.unlink(temp_path)
            
            # Filter out comments and clean up
            lines = []
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    if not line.startswith('-'):
                        line = f"- {line}"
                    lines.append(line)
            
            return '\n'.join(lines)
            
        except Exception as e:
            console.print(f"[red]Error using editor:[/red] {e}")
            return current_rules