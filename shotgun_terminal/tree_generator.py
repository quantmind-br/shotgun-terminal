"""Generate file tree structure similar to the tree command."""

import os
from pathlib import Path
from typing import List, Set

class TreeGenerator:
    """Generate a tree structure representation of the project directory."""
    
    def __init__(self, directory: str):
        self.directory = Path(directory)
        self.tree_chars = {
            'branch': '├── ',
            'last': '└── ',
            'extension': '│   ',
            'space': '    '
        }
    
    def generate_tree(self, included_files: List[str], ignore_patterns: List[str] = None) -> str:
        """
        Generate a tree structure for the given files.
        
        Args:
            included_files: List of relative file paths to include
            ignore_patterns: List of patterns to ignore (unused here, files already filtered)
            
        Returns:
            Tree structure as string
        """
        if not included_files:
            return ""
        
        # Build directory structure from included files
        tree_structure = {}
        
        for file_path in included_files:
            parts = Path(file_path).parts
            current = tree_structure
            
            # Build nested structure
            for i, part in enumerate(parts):
                if part not in current:
                    current[part] = {}
                current = current[part]
        
        # Generate tree string
        project_name = self.directory.name
        lines = [f"{project_name}\\"]
        
        self._build_tree_lines(tree_structure, lines, "", True)
        
        return '\n'.join(lines)
    
    def _build_tree_lines(self, structure: dict, lines: list, prefix: str, is_root: bool = False):
        """Recursively build tree lines."""
        items = sorted(structure.keys())
        
        for i, item in enumerate(items):
            is_last = (i == len(items) - 1)
            
            # Determine prefix for this item
            if is_root:
                current_prefix = self.tree_chars['last'] if is_last else self.tree_chars['branch']
            else:
                current_prefix = prefix + (self.tree_chars['last'] if is_last else self.tree_chars['branch'])
            
            lines.append(current_prefix + item)
            
            # If this item has children (is a directory), recurse
            if structure[item]:
                # Determine prefix for children
                if is_root:
                    child_prefix = self.tree_chars['space'] if is_last else self.tree_chars['extension']
                else:
                    child_prefix = prefix + (self.tree_chars['space'] if is_last else self.tree_chars['extension'])
                
                self._build_tree_lines(structure[item], lines, child_prefix)
    
    def generate_full_tree(self, max_depth: int = 3) -> str:
        """
        Generate a full tree of the directory (for reference).
        
        Args:
            max_depth: Maximum depth to traverse
            
        Returns:
            Tree structure as string
        """
        lines = [f"{self.directory.name}\\"]
        
        try:
            self._traverse_directory(self.directory, lines, "", 0, max_depth, True)
        except Exception:
            # Fallback to simple listing if tree generation fails
            lines.append("├── (files)")
        
        return '\n'.join(lines)
    
    def _traverse_directory(self, directory: Path, lines: list, prefix: str, depth: int, max_depth: int, is_root: bool = False):
        """Traverse directory and build tree."""
        if depth > max_depth:
            return
        
        try:
            items = []
            # Get directories and files separately
            for item in directory.iterdir():
                if not item.name.startswith('.'):  # Skip hidden files/dirs
                    items.append(item)
            
            # Sort: directories first, then files
            items.sort(key=lambda x: (x.is_file(), x.name.lower()))
            
            for i, item in enumerate(items):
                is_last = (i == len(items) - 1)
                
                # Determine prefix for this item
                if is_root:
                    current_prefix = self.tree_chars['last'] if is_last else self.tree_chars['branch']
                else:
                    current_prefix = prefix + (self.tree_chars['last'] if is_last else self.tree_chars['branch'])
                
                lines.append(current_prefix + item.name)
                
                # If directory, recurse
                if item.is_dir() and depth < max_depth:
                    if is_root:
                        child_prefix = self.tree_chars['space'] if is_last else self.tree_chars['extension']
                    else:
                        child_prefix = prefix + (self.tree_chars['space'] if is_last else self.tree_chars['extension'])
                    
                    self._traverse_directory(item, lines, child_prefix, depth + 1, max_depth)
        
        except PermissionError:
            # Skip directories we can't access
            pass