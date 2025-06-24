"""Gemini API integration service."""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

console = Console()

class GeminiService:
    """Service for integrating with Google Gemini API."""
    
    def __init__(self):
        self.client = None
        self.is_configured = False
        
    def configure(self, api_key: str) -> bool:
        """Configure the Gemini client with API key."""
        if not GEMINI_AVAILABLE:
            console.print("[red]Error:[/red] google-genai package not available. Install with: pip install google-genai")
            return False
            
        if not api_key or api_key.strip() == "":
            console.print("[red]Error:[/red] API key is required")
            return False
            
        try:
            # Set environment variable for the API key
            os.environ["GEMINI_API_KEY"] = api_key
            
            # Create client
            self.client = genai.Client(api_key=api_key)
            self.is_configured = True
            
            console.print("[green]✓[/green] Gemini API configured successfully")
            return True
            
        except Exception as e:
            console.print(f"[red]Error configuring Gemini API:[/red] {e}")
            self.is_configured = False
            return False
    
    def test_connection(self) -> bool:
        """Test connection to Gemini API."""
        if not self.is_configured or not self.client:
            console.print("[red]Error:[/red] Gemini API not configured")
            return False
            
        try:
            # Simple test with minimal content
            response = self.client.models.generate_content(
                model='gemini-2.5-pro',
                contents='Test connection',
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=10,
                    response_mime_type="text/plain",
                ),
            )
            
            if response and response.text:
                console.print("[green]✓[/green] Gemini API connection successful")
                return True
            else:
                console.print("[red]Error:[/red] Empty response from Gemini API")
                return False
                
        except Exception as e:
            console.print(f"[red]Error testing Gemini API:[/red] {e}")
            return False
    
    def generate_response(self, prompt: str, temperature: float = 0.35, thinking_budget: int = 32768) -> Optional[str]:
        """Generate response from Gemini API with streaming."""
        if not self.is_configured or not self.client:
            console.print("[red]Error:[/red] Gemini API not configured")
            return None
            
        # Validate parameters
        if not (0.0 <= temperature <= 2.0):
            console.print(f"[red]Error:[/red] Temperature must be between 0.0 and 2.0, got {temperature}")
            return None
            
        if not (0 <= thinking_budget <= 32768):
            console.print(f"[red]Error:[/red] Thinking budget must be between 0 and 32768, got {thinking_budget}")
            return None
            
        try:
            console.print(f"[yellow]🤖 Sending prompt to Gemini API...[/yellow]")
            console.print(f"[dim]Temperature: {temperature}, Thinking Budget: {thinking_budget}[/dim]")
            
            # Prepare content
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt),
                    ],
                ),
            ]
            
            # Configure generation
            generate_content_config = types.GenerateContentConfig(
                temperature=temperature,
                thinking_config=types.ThinkingConfig(
                    thinking_budget=thinking_budget,
                ),
                response_mime_type="text/plain",
            )
            
            # Stream response
            response_parts = []
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                task = progress.add_task("Receiving response from Gemini...", total=None)
                
                for chunk in self.client.models.generate_content_stream(
                    model="gemini-2.5-pro",
                    contents=contents,
                    config=generate_content_config,
                ):
                    if chunk.text:
                        response_parts.append(chunk.text)
                        # Update progress description with latest chunk preview
                        preview = chunk.text[:50].replace('\n', ' ')
                        if len(chunk.text) > 50:
                            preview += "..."
                        progress.update(task, description=f"Receiving: {preview}")
            
            full_response = ''.join(response_parts)
            
            if full_response:
                console.print("[green]✓[/green] Response received successfully")
                console.print(f"[dim]Response length: {len(full_response)} characters[/dim]")
                return full_response
            else:
                console.print("[red]Error:[/red] Empty response from Gemini API")
                return None
                
        except Exception as e:
            console.print(f"[red]Error generating response:[/red] {e}")
            return None
    
    def save_response(self, response: str, output_dir: str = ".") -> Optional[str]:
        """Save Gemini response to a file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"shotgun_response_{timestamp}.txt"
            filepath = Path(output_dir) / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response)
            
            console.print(f"[green]✓[/green] Response saved to: {filepath}")
            return str(filepath)
            
        except Exception as e:
            console.print(f"[red]Error saving response:[/red] {e}")
            return None
    
    def process_prompt(self, prompt: str, temperature: float = 0.35, thinking_budget: int = 32768, 
                      output_dir: str = ".") -> Optional[str]:
        """Complete workflow: generate response and save to file."""
        response = self.generate_response(prompt, temperature, thinking_budget)
        
        if response:
            return self.save_response(response, output_dir)
        
        return None