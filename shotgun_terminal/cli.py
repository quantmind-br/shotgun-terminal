#!/usr/bin/env python3

import click
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
import inquirer

from .prompts import process_template
from .file_selector import FileSelector
from .context_generator import ContextGenerator
from .user_input import UserInputCollector
from .settings import SettingsManager
from .config import ConfigManager
from .translator import TranslationService
from .gemini_service import GeminiService

console = Console()

@click.command()
@click.option('--directory', '-d', type=click.Path(exists=True, file_okay=False, dir_okay=True), 
              help='Project directory to analyze')
@click.option('--output', '-o', type=click.Path(), help='Output file path (default: shotgun_context.txt)')
@click.option('--prompt-type', '-p', type=click.Choice(['dev', 'architect', 'bug']), 
              help='Type of prompt to generate')
@click.option('--config', is_flag=True, help='Configure API settings for translation')
@click.option('--gemini-config', is_flag=True, help='Configure Gemini API settings')
@click.option('--quick-setup', is_flag=True, help='Quick setup with test credentials')
def main(directory, output, prompt_type, config, gemini_config, quick_setup):
    """Shotgun Terminal - Generate comprehensive project context for LLM workflows."""
    
    console.print(Panel.fit(
        "[bold blue]🔫 Shotgun Terminal[/bold blue]\n"
        "Generate comprehensive project context for LLM workflows",
        border_style="blue"
    ))
    
    # Handle configuration commands
    if config or gemini_config or quick_setup:
        config_manager = ConfigManager()
        
        if quick_setup:
            config_manager.quick_setup()
        elif gemini_config:
            config_manager.configure_gemini()
        else:
            config_manager.configure_api()
        
        return
    
    # Initialize components
    settings = SettingsManager()
    user_input = UserInputCollector()
    translator = TranslationService()
    gemini_service = GeminiService()
    
    # Step 1: Select project directory
    if not directory:
        directory = select_directory(settings)
    
    console.print(f"\n[green]✓[/green] Selected directory: {directory}")
    settings.set_last_used_directory(directory)
    
    # Step 2: Collect user task
    console.print("\n" + "="*60)
    user_task = user_input.collect_user_task()
    console.print(f"\n[green]✓[/green] Task collected")
    
    # Step 3: Collect custom rules
    console.print("\n" + "="*60)
    custom_rules = user_input.collect_custom_rules()
    console.print(f"\n[green]✓[/green] Custom rules configured")
    
    # Step 4: Translate task and rules to English (if enabled)
    translation_enabled = settings.is_translation_enabled()
    api_configured = translator.is_configured()
    
    console.print(f"\n[dim]Debug: Translation enabled: {translation_enabled}, API configured: {api_configured}[/dim]")
    
    if translation_enabled and api_configured:
        console.print("\n" + "="*60)
        console.print("[yellow]🌍 Translating to English...[/yellow]")
        
        # Translate task
        if user_task.strip():
            console.print(f"[dim]Original task: {user_task[:50]}...[/dim]")
            translated_task = translator.translate_to_english(user_task, "task")
            
            if translated_task and translated_task != user_task:
                user_task = translated_task
                console.print("[green]✓[/green] Task translated")
                console.print(f"[dim]Translated task: {user_task[:50]}...[/dim]")
            elif translated_task == user_task:
                console.print("[yellow]Task translation was skipped (detected as English)[/yellow]")
                force_translate = Confirm.ask("Force translation anyway?", default=False)
                if force_translate:
                    forced_task = translator.translate_to_english(user_task, "task", force=True)
                    if forced_task and forced_task != user_task:
                        user_task = forced_task
                        console.print("[green]✓[/green] Task force-translated")
                        console.print(f"[dim]Translated task: {user_task[:50]}...[/dim]")
            else:
                console.print("[red]Task translation failed[/red]")
        
        # Translate rules
        if custom_rules.strip():
            console.print(f"[dim]Original rules: {custom_rules[:50]}...[/dim]")
            translated_rules = translator.translate_to_english(custom_rules, "rules")
            
            if translated_rules and translated_rules != custom_rules:
                custom_rules = translated_rules
                console.print("[green]✓[/green] Rules translated")
                console.print(f"[dim]Translated rules: {custom_rules[:50]}...[/dim]")
            elif translated_rules == custom_rules:
                console.print("[yellow]Rules translation was skipped (detected as English)[/yellow]")
                force_translate = Confirm.ask("Force translation anyway?", default=False)
                if force_translate:
                    forced_rules = translator.translate_to_english(custom_rules, "rules", force=True)
                    if forced_rules and forced_rules != custom_rules:
                        custom_rules = forced_rules
                        console.print("[green]✓[/green] Rules force-translated")
                        console.print(f"[dim]Translated rules: {custom_rules[:50]}...[/dim]")
            else:
                console.print("[red]Rules translation failed[/red]")
        
        console.print(f"\n[green]✓[/green] Translation completed")
    elif translation_enabled and not api_configured:
        console.print("\n[yellow]⚠️  Translation enabled but API not configured.[/yellow]")
        console.print("[yellow]Use 'shotgun-terminal --config' to set up translation.[/yellow]")
    else:
        console.print("\n[dim]Translation disabled - using original text[/dim]")
    
    # Step 5: Interactive file selection
    console.print("\n" + "="*60)
    file_selector = FileSelector(directory)
    included_files, ignore_patterns = file_selector.interactive_selection()
    console.print(f"\n[green]✓[/green] Files selected")
    
    # Step 6: Select prompt type
    if not prompt_type:
        console.print("\n" + "="*60)
        prompt_type = select_prompt_type()
    
    # Step 7: Generate output file path
    if not output:
        output = f"shotgun_context_{prompt_type}.txt"
    
    # Step 8: Generate context
    console.print("\n" + "="*60)
    console.print(f"[yellow]Generating context...[/yellow]")
    final_output = generate_context(directory, included_files, ignore_patterns, prompt_type, output, user_task, custom_rules)
    
    # Step 9: Check if Gemini is enabled and process if so
    if settings.is_gemini_enabled():
        console.print("\n" + "="*60)
        console.print("[yellow]🤖 Gemini integration enabled - processing prompt...[/yellow]")
        
        api_key = settings.get_gemini_api_key()
        if api_key:
            # Configure Gemini service
            if gemini_service.configure(api_key):
                # Get Gemini settings
                temperature = settings.get_gemini_temperature()
                thinking_budget = settings.get_gemini_thinking_budget()
                
                # Process with Gemini
                gemini_output_file = gemini_service.process_prompt(
                    final_output, 
                    temperature=temperature, 
                    thinking_budget=thinking_budget,
                    output_dir=os.path.dirname(output) if output else "."
                )
                
                if gemini_output_file:
                    console.print(f"\n[bold green]🎉 Gemini Processing Complete![/bold green]")
                    console.print(f"[green]✓[/green] Context generated and processed by Gemini")
                    console.print(f"[green]✓[/green] Original context saved to: {output}")
                    console.print(f"[green]✓[/green] Gemini response saved to: {gemini_output_file}")
                    
                    # Show Gemini summary
                    show_gemini_summary(gemini_output_file, user_task, len(included_files), temperature, thinking_budget)
                else:
                    console.print(f"\n[yellow]⚠️  Gemini processing failed - using standard output[/yellow]")
                    console.print(f"[green]✓[/green] Context generated successfully!")
                    console.print(f"[green]✓[/green] Output saved to: {output}")
                    show_summary(output, user_task, len(included_files))
            else:
                console.print(f"\n[yellow]⚠️  Failed to configure Gemini - using standard output[/yellow]")
                console.print(f"[green]✓[/green] Context generated successfully!")
                console.print(f"[green]✓[/green] Output saved to: {output}")
                show_summary(output, user_task, len(included_files))
        else:
            console.print(f"\n[yellow]⚠️  Gemini enabled but no API key configured - using standard output[/yellow]")
            console.print(f"[green]✓[/green] Context generated successfully!")
            console.print(f"[green]✓[/green] Output saved to: {output}")
            show_summary(output, user_task, len(included_files))
    else:
        console.print(f"\n[bold green]🎉 Success![/bold green]")
        console.print(f"[green]✓[/green] Context generated successfully!")
        console.print(f"[green]✓[/green] Output saved to: {output}")
        
        # Show final summary
        show_summary(output, user_task, len(included_files))


def select_directory(settings):
    """Interactive directory selection."""
    current_dir = os.getcwd()
    last_used = settings.get_last_used_directory()
    
    console.print(f"\n[yellow]Current directory:[/yellow] {current_dir}")
    if last_used and last_used != current_dir:
        console.print(f"[blue]Last used directory:[/blue] {last_used}")
    
    choices = ["Use current directory"]
    if last_used and last_used != current_dir and os.path.exists(last_used):
        choices.append("Use last used directory")
    choices.append("Enter custom path")
    
    choice = inquirer.list_input("Select directory", choices=choices)
    
    if choice == "Use current directory":
        return current_dir
    elif choice == "Use last used directory":
        return last_used
    else:
        directory = Prompt.ask("Enter project directory path")
        
        if not os.path.exists(directory):
            console.print(f"[red]Error:[/red] Directory {directory} does not exist")
            return select_directory(settings)
        
        return directory


def select_prompt_type():
    """Interactive prompt type selection."""
    console.print("\n[yellow]Select prompt type:[/yellow]")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Type", style="dim", width=12)
    table.add_column("Description")
    
    table.add_row("dev", "General development assistance and code analysis")
    table.add_row("architect", "Architecture review and system design")
    table.add_row("bug", "Bug analysis and debugging assistance")
    
    console.print(table)
    
    questions = [
        inquirer.List('prompt_type',
                     message="Choose prompt type",
                     choices=[
                         ('dev - General development assistance', 'dev'),
                         ('architect - Architecture review', 'architect'), 
                         ('bug - Bug analysis and debugging', 'bug')
                     ])
    ]
    
    answers = inquirer.prompt(questions)
    return answers['prompt_type']


def generate_context(directory, included_files, ignore_patterns, prompt_type, output_file, user_task, custom_rules):
    """Generate context using internal Python implementation."""
    
    try:
        # Create context generator
        generator = ContextGenerator(directory)
        
        # Show file statistics
        stats = generator.get_file_stats(included_files, ignore_patterns)
        console.print(f"[blue]Files to process: {stats['total_files']}[/blue]")
        console.print(f"[blue]Total size: {stats['total_size'] / 1024:.1f} KB[/blue]")
        
        if stats['large_files']:
            console.print(f"[yellow]Large files (will be skipped): {len(stats['large_files'])}[/yellow]")
        
        if stats['binary_files']:
            console.print(f"[yellow]Binary files (will be summarized): {len(stats['binary_files'])}[/yellow]")
        
        # Generate project tree
        project_tree = generator.generate_project_tree(included_files, ignore_patterns)
        
        # Generate context
        context = generator.generate_context(included_files, ignore_patterns, 'claude-xml')
        
        # Process template with user inputs
        final_output = process_template(prompt_type, user_task, custom_rules, context, project_tree)
        
        # Write to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_output)
        
        # Return the final output for potential Gemini processing
        return final_output
            
    except Exception as e:
        console.print(f"[red]Error generating context:[/red] {e}")
        raise


def show_gemini_summary(gemini_output_file, user_task, file_count, temperature, thinking_budget):
    """Show final summary with Gemini processing details."""
    console.print(Panel.fit(
        f"[bold green]🤖 Gemini Processing Summary[/bold green]\n\n"
        f"[blue]Task:[/blue] {user_task[:100]}{'...' if len(user_task) > 100 else ''}\n"
        f"[blue]Files processed:[/blue] {file_count}\n"
        f"[blue]Temperature:[/blue] {temperature}\n"
        f"[blue]Thinking Budget:[/blue] {thinking_budget}\n"
        f"[blue]Gemini Response:[/blue] {gemini_output_file}\n\n"
        f"[dim]The prompt has been automatically processed by Gemini AI. "
        f"Check the response file for the generated content.[/dim]",
        border_style="green"
    ))


def show_summary(output_file, user_task, file_count):
    """Show final summary of the generated context."""
    console.print(Panel.fit(
        f"[bold green]📄 Context Summary[/bold green]\n\n"
        f"[blue]Task:[/blue] {user_task[:100]}{'...' if len(user_task) > 100 else ''}\n"
        f"[blue]Files processed:[/blue] {file_count}\n"
        f"[blue]Output file:[/blue] {output_file}\n\n"
        f"[dim]You can now copy the content from {output_file} and paste it into your preferred LLM interface.[/dim]",
        border_style="green"
    ))


if __name__ == '__main__':
    main()