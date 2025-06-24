"""Rich-based hierarchical file tree selector with checkboxes."""

import os
import sys
import fnmatch
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple

# Platform-specific imports for key capture
try:
    import termios
    import tty
    UNIX_AVAILABLE = True
except ImportError:
    UNIX_AVAILABLE = False

try:
    import msvcrt
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False
from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

console = Console()

# Unicode checkbox symbols
SELECTED = "☑"  # Selected for inclusion in prompt
UNSELECTED = "☐"  # Not selected for inclusion
IGNORED = "☒"  # Ignored by default patterns
DIRECTORY = "📁"  # Directory icon
FILE = "📄"  # File icon


def get_key():
    """Get a single keypress from stdin."""
    if os.name == 'nt' and WINDOWS_AVAILABLE:  # Windows
        key = msvcrt.getch()
        if key == b'\xe0':  # Arrow keys on Windows
            key = msvcrt.getch()
            if key == b'H':
                return 'up'
            elif key == b'P':
                return 'down'
            elif key == b'K':
                return 'left'
            elif key == b'M':
                return 'right'
        elif key == b'\r':
            return 'enter'
        elif key == b' ':
            return 'space'
        elif key == b'\x1b':  # ESC
            return 'esc'
        elif key in [b'\x03', b'\x04']:  # Ctrl+C, Ctrl+D
            return 'quit'
        else:
            return key.decode('utf-8', 'ignore').lower()
    elif UNIX_AVAILABLE:  # Unix/Linux/macOS
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
            
            if key == '\x1b':  # ESC sequence
                key += sys.stdin.read(2)
                if key == '\x1b[A':
                    return 'up'
                elif key == '\x1b[B':
                    return 'down'
                elif key == '\x1b[C':
                    return 'right'
                elif key == '\x1b[D':
                    return 'left'
                else:
                    return 'esc'
            elif key == '\r' or key == '\n':
                return 'enter'
            elif key == ' ':
                return 'space'
            elif key in ['\x03', '\x04']:  # Ctrl+C, Ctrl+D
                return 'quit'
            else:
                return key.lower()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    else:
        # Fallback for platforms without termios or msvcrt
        console.print("[yellow]Warning: Advanced key capture not available on this platform.[/yellow]")
        console.print("[yellow]Using basic input mode. Press Enter after each key.[/yellow]")
        key = input("Key: ").strip().lower()
        if key in ['up', 'down', 'left', 'right', 'space', 'enter', 'q', 'quit']:
            return key
        elif key == '':
            return 'enter'
        else:
            return key


class ShotgunIgnoreManager:
    """Manages .shotgunignore file for persistent file exclusion."""

    def __init__(self, directory: Path):
        self.directory = Path(directory)
        self.ignore_file = self.directory / ".shotgunignore"
        self.default_patterns = [
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
            ".shotgunignore",
        ]

    def read_ignore_patterns(self) -> Set[str]:
        """Read ignore patterns from .shotgunignore file."""
        patterns = set(self.default_patterns)

        if self.ignore_file.exists():
            try:
                with open(self.ignore_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            patterns.add(line)
            except Exception as e:
                console.print(
                    f"[yellow]Warning:[/yellow] Could not read .shotgunignore: {e}"
                )

        return patterns

    def write_ignore_patterns(self, patterns: Set[str]) -> bool:
        """Write ignore patterns to .shotgunignore file."""
        try:
            # Remove default patterns to keep file clean
            custom_patterns = patterns - set(self.default_patterns)

            with open(self.ignore_file, "w", encoding="utf-8") as f:
                f.write("# Shotgun Terminal ignore patterns\n")
                f.write("# This file is auto-generated. Edit with caution.\n\n")

                # Write default patterns as comments for reference
                f.write("# Default patterns (always applied):\n")
                for pattern in sorted(self.default_patterns):
                    f.write(f"# {pattern}\n")

                if custom_patterns:
                    f.write("\n# Custom patterns:\n")
                    for pattern in sorted(custom_patterns):
                        f.write(f"{pattern}\n")

            console.print(
                f"[green]✓[/green] Saved ignore patterns to {self.ignore_file}"
            )
            return True

        except Exception as e:
            console.print(f"[red]Error:[/red] Could not write .shotgunignore: {e}")
            return False

    def should_ignore(self, file_path: Path, patterns: Set[str]) -> bool:
        """Check if a file should be ignored based on patterns."""
        relative_path = file_path.relative_to(self.directory)
        path_str = str(relative_path)

        for pattern in patterns:
            # Direct match
            if fnmatch.fnmatch(path_str, pattern):
                return True

            # Directory match (for folder patterns ending with /)
            if pattern.endswith("/") and (
                path_str.startswith(pattern) or fnmatch.fnmatch(path_str + "/", pattern)
            ):
                return True

            # Parent directory match
            if "/" in pattern:
                parts = Path(pattern).parts
                path_parts = relative_path.parts
                if len(parts) <= len(path_parts):
                    match = True
                    for i, part in enumerate(parts):
                        if not fnmatch.fnmatch(path_parts[i], part):
                            match = False
                            break
                    if match:
                        return True

        return False


class FileNode:
    """Represents a file or directory node in the tree."""

    def __init__(
        self,
        path: Path,
        is_directory: bool = False,
        parent: Optional["FileNode"] = None,
    ):
        self.path = path
        self.is_directory = is_directory
        self.parent = parent
        self.children: List["FileNode"] = []
        self.checked = True  # All files start checked
        self.expanded = True if is_directory else False

    def add_child(self, child: "FileNode"):
        """Add a child node."""
        child.parent = self
        self.children.append(child)

    def set_checked(self, checked: bool, recursive: bool = True):
        """Set checked state, optionally affecting children."""
        self.checked = checked

        if recursive and self.is_directory:
            for child in self.children:
                child.set_checked(checked, recursive=True)

    def get_all_files(self) -> List["FileNode"]:
        """Get all file nodes (not directories) in this subtree."""
        files = []
        if not self.is_directory:
            files.append(self)

        for child in self.children:
            files.extend(child.get_all_files())

        return files

    def get_unchecked_patterns(self, base_path: Path) -> Set[str]:
        """Get ignore patterns for unchecked items."""
        patterns = set()

        if not self.checked:
            relative_path = self.path.relative_to(base_path)
            if self.is_directory:
                patterns.add(str(relative_path) + "/")
            else:
                patterns.add(str(relative_path))
        else:
            # Check children only if this node is checked
            for child in self.children:
                patterns.update(child.get_unchecked_patterns(base_path))

        return patterns


class RichFileTreeSelector:
    """Rich-based file tree selector with checkboxes."""

    def __init__(self, directory: Path):
        self.directory = Path(directory)
        self.ignore_manager = ShotgunIgnoreManager(directory)
        self.root_node = None
        self.flat_list = []  # Flattened list for navigation
        self.current_index = 0
        self.visible_items = []  # Currently visible items

    def build_file_tree(self) -> FileNode:
        """Build the file tree structure."""
        ignore_patterns = self.ignore_manager.read_ignore_patterns()

        def build_node(
            path: Path, parent: Optional[FileNode] = None
        ) -> Optional[FileNode]:
            # Skip if should be ignored by default patterns (but not custom ones)
            if self.ignore_manager.should_ignore(
                path, set(self.ignore_manager.default_patterns)
            ):
                return None

            is_dir = path.is_dir()
            node = FileNode(path, is_dir, parent)

            # Set initial checked state based on ignore patterns
            if self.ignore_manager.should_ignore(path, ignore_patterns):
                node.checked = False

            if is_dir:
                try:
                    for child_path in sorted(path.iterdir()):
                        child_node = build_node(child_path, node)
                        if child_node:
                            node.add_child(child_node)
                except PermissionError:
                    pass  # Skip directories we can't read

            return node

        return build_node(self.directory)

    def flatten_tree(
        self, node: FileNode, level: int = 0
    ) -> List[Tuple[FileNode, int]]:
        """Flatten tree into a navigable list."""
        items = []

        # Always include children of root, but not root itself
        if node.path == self.directory:
            # For root directory, include all children
            for child in node.children:
                items.extend(self.flatten_tree(child, level))
        else:
            # Include this node
            items.append((node, level))

            # Include children if directory is expanded
            if node.is_directory and node.expanded:
                for child in node.children:
                    items.extend(self.flatten_tree(child, level + 1))

        return items

    def get_checkbox_symbol(self, node: FileNode) -> str:
        """Get the appropriate checkbox symbol for a node."""
        ignore_patterns = self.ignore_manager.read_ignore_patterns()

        # Check if ignored by default patterns
        if self.ignore_manager.should_ignore(
            node.path, set(self.ignore_manager.default_patterns)
        ):
            return IGNORED

        # Check if explicitly ignored in .shotgunignore
        if not node.checked:
            return UNSELECTED

        return SELECTED

    def render_tree(self):
        """Render the current tree state."""
        console.clear()

        # Header
        header = Panel.fit(
            "[bold cyan]🔫 Shotgun File Selector[/bold cyan]\n"
            f"Directory: {self.directory}",
            border_style="cyan",
        )
        console.print(header)

        # Tree display
        tree_lines = []
        for i, (node, level) in enumerate(self.visible_items):
            # Indentation
            indent = "  " * level

            # Checkbox symbol
            checkbox = self.get_checkbox_symbol(node)

            # Icon
            icon = DIRECTORY if node.is_directory else FILE

            # Name
            name = node.path.name

            # Expansion indicator for directories
            expand_indicator = ""
            if node.is_directory:
                expand_indicator = "▼ " if node.expanded else "▶ "

            # Highlight current line
            line_text = f"{indent}{expand_indicator}{checkbox} {icon} {name}"
            if i == self.current_index:
                line_text = f"[reverse]{line_text}[/reverse]"

            tree_lines.append(line_text)

        # Display tree in a panel
        tree_content = "\n".join(tree_lines) if tree_lines else "No files found"
        tree_panel = Panel(
            tree_content,
            title="[bold]File Tree[/bold]",
            border_style="blue",
            height=20,
        )
        console.print(tree_panel)

        # Instructions
        instructions = Panel.fit(
            "[bold]Navigation:[/bold]\n"
            "↑↓/K/J Navigate  [bold]Space[/bold] Toggle  [bold]Enter[/bold] Expand/Collapse\n"
            "[bold]A[/bold] Select All  [bold]N[/bold] Select None  [bold]S[/bold] Save & Continue  [bold]Q[/bold] Quit  [bold]H[/bold] Help",
            border_style="green",
        )
        console.print(instructions)

        # Stats
        if self.root_node:
            all_files = self.root_node.get_all_files()
            selected_count = sum(1 for f in all_files if f.checked)
            total_count = len(all_files)

            stats_text = f"[dim]Files: {selected_count}/{total_count} selected[/dim]"
            console.print(Align.center(stats_text))

    def handle_input(self) -> bool:
        """Handle user input. Returns False to quit."""
        try:
            console.print("\n[dim]Press any key (↑↓ to navigate, Space to toggle, Enter to expand, S to save, Q to quit, H for help)[/dim]")
            key = get_key()

            if key in ["q", "quit"]:
                return False
            elif key == "s":
                return self.save_and_continue()
            elif key in ["up", "k"]:
                self.navigate_up()
            elif key in ["down", "j"]:
                self.navigate_down()
            elif key == "space":
                self.toggle_current()
            elif key == "enter":
                self.expand_collapse_current()
            elif key == "a":
                self.select_all()
            elif key == "n":
                self.select_none()
            elif key in ["h", "?"]:
                self.show_help()
            elif key == "esc":
                return False

            return True

        except KeyboardInterrupt:
            return False
        except Exception as e:
            console.print(f"[red]Input error:[/red] {e}")
            return True

    def navigate_up(self):
        """Navigate to previous item."""
        if self.current_index > 0:
            self.current_index -= 1

    def navigate_down(self):
        """Navigate to next item."""
        if self.current_index < len(self.visible_items) - 1:
            self.current_index += 1

    def toggle_current(self):
        """Toggle selection of current item."""
        if self.visible_items and self.current_index < len(self.visible_items):
            node, _ = self.visible_items[self.current_index]
            node.set_checked(not node.checked, recursive=True)

    def expand_collapse_current(self):
        """Expand or collapse current directory."""
        if self.visible_items and self.current_index < len(self.visible_items):
            node, _ = self.visible_items[self.current_index]
            if node.is_directory:
                node.expanded = not node.expanded
                self.update_visible_items()

    def select_all(self):
        """Select all files."""
        if self.root_node:
            self.root_node.set_checked(True, recursive=True)

    def select_none(self):
        """Deselect all files."""
        if self.root_node:
            self.root_node.set_checked(False, recursive=True)

    def update_visible_items(self):
        """Update the visible items list."""
        if self.root_node:
            self.visible_items = self.flatten_tree(self.root_node)
            # Ensure current index is within bounds
            if self.current_index >= len(self.visible_items):
                self.current_index = max(0, len(self.visible_items) - 1)

    def show_help(self):
        """Show help information."""
        help_text = """
[bold cyan]Shotgun File Selector Help[/bold cyan]

[bold]Navigation:[/bold]
  ↑, k        - Move cursor up
  ↓, j        - Move cursor down
  
[bold]Selection:[/bold]
  Space       - Toggle selection of current item
  Enter       - Expand/collapse directory
  A           - Select all files
  N           - Deselect all files
  
[bold]Actions:[/bold]
  S           - Save selections and continue
  Q, Esc      - Quit without saving
  H, ?        - Show this help

[bold]Symbols:[/bold]
  ☑ - Selected for inclusion in prompt
  ☐ - Not selected for inclusion  
  ☒ - Ignored by default patterns
  📁 - Directory
  📄 - File
  ▶ - Collapsed directory
  ▼ - Expanded directory
"""
        console.print(Panel(help_text, border_style="yellow"))
        console.print("[dim]Press any key to continue...[/dim]")
        get_key()

    def save_and_continue(self) -> bool:
        """Save selections and exit."""
        if not self.root_node:
            console.print("[red]Error:[/red] No files to save")
            return True

        ignore_patterns = self.root_node.get_unchecked_patterns(self.directory)
        # Add default patterns
        ignore_patterns.update(self.ignore_manager.default_patterns)

        if self.ignore_manager.write_ignore_patterns(ignore_patterns):
            selected_files = [
                node.path for node in self.root_node.get_all_files() if node.checked
            ]
            console.print(f"[green]✓[/green] Selected {len(selected_files)} files")
            return False  # Exit the loop
        else:
            console.print("[red]Error:[/red] Failed to save ignore patterns")
            return True

    def run(self) -> List[Path]:
        """Run the file selector and return selected files."""
        console.print("[cyan]Building file tree...[/cyan]")

        self.root_node = self.build_file_tree()
        if not self.root_node:
            console.print("[red]Error:[/red] Could not build file tree")
            return []

        self.update_visible_items()

        if not self.visible_items:
            console.print("[yellow]Warning:[/yellow] No files found")
            return []

        console.print("[green]✓[/green] File tree built successfully")
        console.print("[dim]Use 'help' command for navigation instructions[/dim]")

        # Main interaction loop
        try:
            while True:
                self.render_tree()
                if not self.handle_input():
                    break
        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled[/yellow]")
            return []

        # Return selected files
        if self.root_node:
            selected_files = [
                node.path for node in self.root_node.get_all_files() if node.checked
            ]
            return selected_files

        return []


def run_hierarchical_selector(directory: Path) -> List[Path]:
    """Run the hierarchical file selector and return selected files."""
    try:
        selector = RichFileTreeSelector(directory)
        return selector.run()
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to run hierarchical selector: {e}")
        return []


def run_simple_selector(directory: Path) -> List[Path]:
    """Simple fallback file selector using basic file listing."""
    console.print("[yellow]Using simple file selector[/yellow]")

    ignore_manager = ShotgunIgnoreManager(directory)
    ignore_patterns = ignore_manager.read_ignore_patterns()

    # Get all files
    all_files = []
    for root, dirs, files in os.walk(directory):
        # Remove ignored directories from dirs to prevent traversal
        dirs[:] = [
            d
            for d in dirs
            if not ignore_manager.should_ignore(
                Path(root) / d, set(ignore_manager.default_patterns)
            )
        ]

        for file in files:
            file_path = Path(root) / file
            if not ignore_manager.should_ignore(
                file_path, set(ignore_manager.default_patterns)
            ):
                all_files.append(file_path)

    # Filter out files that should be ignored based on .shotgunignore
    selected_files = [
        f for f in all_files if not ignore_manager.should_ignore(f, ignore_patterns)
    ]

    console.print(
        f"[green]✓[/green] Found {len(selected_files)} files (filtered by .shotgunignore)"
    )
    return selected_files
