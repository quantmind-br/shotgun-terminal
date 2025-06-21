"""Interactive file selection module."""

import os
import fnmatch
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm, Prompt
import inquirer

console = Console()

class FileSelector:
    """Interactive file selector with ignore pattern support."""
    
    def __init__(self, directory):
        self.directory = Path(directory)
        self.default_ignore_patterns = [
            '*.pyc',
            '__pycache__',
            '.git',
            '.gitignore',
            '*.log',
            'node_modules',
            '.env',
            '*.tmp',
            '.DS_Store',
            'build',
            'dist',
            '*.egg-info'
        ]
    
    def interactive_selection(self):
        """Interactive file selection process."""
        console.print(f"\n[yellow]Analyzing directory:[/yellow] {self.directory}")
        
        # Get all files
        all_files = self._get_all_files()
        
        console.print(f"[blue]Found {len(all_files)} files[/blue]")
        
        # Show file overview
        self._show_file_overview(all_files)
        
        # Configure ignore patterns
        ignore_patterns = self._configure_ignore_patterns()
        
        # Apply ignore patterns
        filtered_files = self._apply_ignore_patterns(all_files, ignore_patterns)
        
        console.print(f"\n[green]Selected {len(filtered_files)} files after filtering[/green]")
        
        # Optional: Manual file review
        if Confirm.ask("Review and modify file selection manually?", default=False):
            filtered_files = self._manual_file_selection(filtered_files)
        
        return filtered_files, ignore_patterns
    
    def _get_all_files(self):
        """Get all files in directory recursively."""
        files = []
        for root, dirs, filenames in os.walk(self.directory):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for filename in filenames:
                if not filename.startswith('.'):
                    file_path = Path(root) / filename
                    rel_path = file_path.relative_to(self.directory)
                    files.append(str(rel_path))
        
        return sorted(files)
    
    def _show_file_overview(self, files):
        """Show overview of files by extension."""
        extensions = {}
        for file in files:
            ext = Path(file).suffix or 'no extension'
            extensions[ext] = extensions.get(ext, 0) + 1
        
        table = Table(title="File Overview by Extension")
        table.add_column("Extension", style="cyan")
        table.add_column("Count", style="magenta")
        
        for ext, count in sorted(extensions.items(), key=lambda x: x[1], reverse=True):
            table.add_row(ext, str(count))
        
        console.print(table)
    
    def _configure_ignore_patterns(self):
        """Configure ignore patterns interactively."""
        console.print(f"\n[yellow]Current ignore patterns:[/yellow]")
        
        for i, pattern in enumerate(self.default_ignore_patterns, 1):
            console.print(f"{i:2}. {pattern}")
        
        # Ask if user wants to modify patterns
        modify = Confirm.ask("\nModify ignore patterns?", default=False)
        
        if not modify:
            return self.default_ignore_patterns.copy()
        
        ignore_patterns = self.default_ignore_patterns.copy()
        
        while True:
            action = inquirer.list_input(
                "Choose action",
                choices=[
                    'Add pattern',
                    'Remove pattern', 
                    'View current patterns',
                    'Done'
                ]
            )
            
            if action == 'Add pattern':
                pattern = Prompt.ask("Enter ignore pattern (e.g., '*.log', 'temp/')")
                if pattern:
                    ignore_patterns.append(pattern)
                    console.print(f"[green]Added:[/green] {pattern}")
            
            elif action == 'Remove pattern':
                if ignore_patterns:
                    questions = [
                        inquirer.Checkbox('patterns',
                                        message="Select patterns to remove",
                                        choices=ignore_patterns)
                    ]
                    answers = inquirer.prompt(questions)
                    for pattern in answers['patterns']:
                        ignore_patterns.remove(pattern)
                        console.print(f"[red]Removed:[/red] {pattern}")
                else:
                    console.print("[yellow]No patterns to remove[/yellow]")
            
            elif action == 'View current patterns':
                console.print(f"\n[yellow]Current patterns:[/yellow]")
                for pattern in ignore_patterns:
                    console.print(f"  • {pattern}")
                console.print()
            
            elif action == 'Done':
                break
        
        return ignore_patterns
    
    def _apply_ignore_patterns(self, files, ignore_patterns):
        """Apply ignore patterns to file list."""
        filtered_files = []
        
        for file in files:
            should_ignore = False
            
            for pattern in ignore_patterns:
                if fnmatch.fnmatch(file, pattern) or fnmatch.fnmatch(os.path.basename(file), pattern):
                    should_ignore = True
                    break
                
                # Check if any parent directory matches pattern
                parts = Path(file).parts
                for part in parts:
                    if fnmatch.fnmatch(part, pattern):
                        should_ignore = True
                        break
                
                if should_ignore:
                    break
            
            if not should_ignore:
                filtered_files.append(file)
        
        return filtered_files
    
    def _manual_file_selection(self, files):
        """Manual file selection interface."""
        console.print(f"\n[yellow]Manual file selection - {len(files)} files[/yellow]")
        
        # Show files in groups for easier selection
        page_size = 20
        selected_files = files.copy()
        
        while True:
            action = inquirer.list_input(
                "Choose action",
                choices=[
                    'View selected files',
                    'Remove files by pattern',
                    'Remove specific files',
                    'Add back files',
                    'Done'
                ]
            )
            
            if action == 'View selected files':
                self._show_file_list(selected_files)
            
            elif action == 'Remove files by pattern':
                pattern = Prompt.ask("Enter pattern to remove (e.g., '*.test.js')")
                if pattern:
                    before_count = len(selected_files)
                    selected_files = [f for f in selected_files 
                                    if not fnmatch.fnmatch(f, pattern)]
                    removed_count = before_count - len(selected_files)
                    console.print(f"[red]Removed {removed_count} files[/red]")
            
            elif action == 'Remove specific files':
                if len(selected_files) > 50:
                    console.print("[yellow]Too many files for individual selection. Use pattern removal instead.[/yellow]")
                else:
                    questions = [
                        inquirer.Checkbox('files',
                                        message="Select files to remove",
                                        choices=selected_files[:50])  # Limit for usability
                    ]
                    answers = inquirer.prompt(questions)
                    for file in answers['files']:
                        selected_files.remove(file)
                    console.print(f"[red]Removed {len(answers['files'])} files[/red]")
            
            elif action == 'Add back files':
                excluded_files = [f for f in files if f not in selected_files]
                if excluded_files:
                    if len(excluded_files) > 50:
                        console.print("[yellow]Too many excluded files. Use pattern matching to add back.[/yellow]")
                        pattern = Prompt.ask("Enter pattern to add back (e.g., '*.py')")
                        if pattern:
                            added_files = [f for f in excluded_files 
                                         if fnmatch.fnmatch(f, pattern)]
                            selected_files.extend(added_files)
                            console.print(f"[green]Added back {len(added_files)} files[/green]")
                    else:
                        questions = [
                            inquirer.Checkbox('files',
                                            message="Select files to add back",
                                            choices=excluded_files)
                        ]
                        answers = inquirer.prompt(questions)
                        selected_files.extend(answers['files'])
                        console.print(f"[green]Added back {len(answers['files'])} files[/green]")
                else:
                    console.print("[yellow]No excluded files to add back[/yellow]")
            
            elif action == 'Done':
                break
        
        return sorted(selected_files)
    
    def _show_file_list(self, files):
        """Show list of files in a formatted way."""
        console.print(f"\n[blue]Selected files ({len(files)}):[/blue]")
        
        for i, file in enumerate(files[:50], 1):  # Show first 50
            console.print(f"{i:3}. {file}")
        
        if len(files) > 50:
            console.print(f"... and {len(files) - 50} more files")
        
        console.print()