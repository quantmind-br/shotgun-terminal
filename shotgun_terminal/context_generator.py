"""Context generation module using Python implementation."""

import os
import fnmatch
from pathlib import Path
from rich.console import Console
from .tree_generator import TreeGenerator

console = Console()


class ContextGenerator:
    """Generate project context without external command dependencies."""

    def __init__(self, directory):
        self.directory = Path(directory)
        self.max_file_size = 1024 * 1024  # 1MB per file limit
        self.max_total_size = 10 * 1024 * 1024  # 10MB total limit
        self.tree_generator = TreeGenerator(directory)

    def generate_context(
        self, included_files, ignore_patterns, format_type="claude-xml"
    ):
        """Generate context from included files."""

        if format_type == "claude-xml":
            return self._generate_claude_xml_format(included_files, ignore_patterns)
        else:
            return self._generate_default_format(included_files, ignore_patterns)

    def _generate_claude_xml_format(self, included_files, ignore_patterns):
        """Generate context in Claude XML format."""

        output_lines = []
        total_size = 0
        processed_files = 0

        # Start with files directly (no header needed)

        for file_path in included_files:
            if self._should_ignore_file(file_path, ignore_patterns):
                continue

            full_path = self.directory / file_path

            if not full_path.is_file():
                continue

            try:
                # Check file size
                file_size = full_path.stat().st_size
                if file_size > self.max_file_size:
                    console.print(
                        f"[yellow]Skipping large file:[/yellow] {file_path} ({file_size} bytes)"
                    )
                    continue

                # Check total size limit
                if total_size + file_size > self.max_total_size:
                    console.print(
                        f"[yellow]Reached size limit. Processed {processed_files} files.[/yellow]"
                    )
                    break

                # Read file content
                content = self._read_file_safely(full_path)
                if content is None:
                    continue

                # Add to output in Claude XML format
                output_lines.append(f'<file path="{file_path}">')
                output_lines.append(content)
                output_lines.append("</file>")
                output_lines.append("")

                total_size += file_size
                processed_files += 1

                if processed_files % 10 == 0:
                    console.print(f"[blue]Processed {processed_files} files...[/blue]")

            except Exception as e:
                console.print(f"[red]Error processing {file_path}:[/red] {e}")
                continue

        console.print(f"[green]Successfully processed {processed_files} files[/green]")
        return "\n".join(output_lines)

    def _generate_default_format(self, included_files, ignore_patterns):
        """Generate context in default format."""

        output_lines = []
        total_size = 0
        processed_files = 0

        for file_path in included_files:
            if self._should_ignore_file(file_path, ignore_patterns):
                continue

            full_path = self.directory / file_path

            if not full_path.is_file():
                continue

            try:
                # Check file size
                file_size = full_path.stat().st_size
                if file_size > self.max_file_size:
                    console.print(
                        f"[yellow]Skipping large file:[/yellow] {file_path} ({file_size} bytes)"
                    )
                    continue

                # Check total size limit
                if total_size + file_size > self.max_total_size:
                    console.print(
                        f"[yellow]Reached size limit. Processed {processed_files} files.[/yellow]"
                    )
                    break

                # Read file content
                content = self._read_file_safely(full_path)
                if content is None:
                    continue

                # Add to output in default format
                output_lines.append(f"--- {file_path} ---")
                output_lines.append(content)
                output_lines.append("")

                total_size += file_size
                processed_files += 1

                if processed_files % 10 == 0:
                    console.print(f"[blue]Processed {processed_files} files...[/blue]")

            except Exception as e:
                console.print(f"[red]Error processing {file_path}:[/red] {e}")
                continue

        console.print(f"[green]Successfully processed {processed_files} files[/green]")
        return "\n".join(output_lines)

    def _should_ignore_file(self, file_path, ignore_patterns):
        """Check if file should be ignored based on patterns."""

        for pattern in ignore_patterns:
            if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(
                os.path.basename(file_path), pattern
            ):
                return True

            # Check if any parent directory matches pattern
            parts = Path(file_path).parts
            for part in parts:
                if fnmatch.fnmatch(part, pattern):
                    return True

        return False

    def _read_file_safely(self, file_path):
        """Read file content safely with encoding detection."""

        # Try different encodings
        encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]

        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    content = f.read()

                # Check if it's a binary file (contains null bytes)
                if "\x00" in content:
                    return f"<Binary file: {file_path.suffix} file>"

                return content

            except UnicodeDecodeError:
                continue
            except Exception as e:
                console.print(f"[red]Error reading {file_path}:[/red] {e}")
                return None

        # If all encodings fail, treat as binary
        return f"<Binary file: {file_path.suffix} file>"

    def get_file_stats(self, included_files, ignore_patterns):
        """Get statistics about files to be processed."""

        stats = {
            "total_files": 0,
            "total_size": 0,
            "file_types": {},
            "large_files": [],
            "binary_files": [],
        }

        for file_path in included_files:
            if self._should_ignore_file(file_path, ignore_patterns):
                continue

            full_path = self.directory / file_path

            if not full_path.is_file():
                continue

            try:
                file_size = full_path.stat().st_size
                file_ext = full_path.suffix or "no extension"

                stats["total_files"] += 1
                stats["total_size"] += file_size
                stats["file_types"][file_ext] = stats["file_types"].get(file_ext, 0) + 1

                if file_size > self.max_file_size:
                    stats["large_files"].append((file_path, file_size))

                # Quick binary check
                try:
                    with open(full_path, "rb") as f:
                        sample = f.read(1024)
                    if b"\x00" in sample:
                        stats["binary_files"].append(file_path)
                except OSError:
                    pass

            except Exception:
                continue

        return stats

    def generate_project_tree(self, included_files, ignore_patterns):
        """Generate project tree structure."""
        return self.tree_generator.generate_tree(included_files, ignore_patterns)
