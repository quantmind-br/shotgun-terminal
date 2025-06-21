#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="shotgun-terminal",
    version="0.1.0",
    author="Shotgun Code Team",
    description="Terminal version of Shotgun - Generate comprehensive project context for LLM workflows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "rich>=10.0.0",
        "inquirer>=2.8.0",
        "openai>=1.0.0",
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "shotgun-terminal=shotgun_terminal.cli:main",
        ],
    },
)