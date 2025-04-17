"""
Cybercare package installation script.

This script handles the installation of the Cybercare package and its dependencies.
It uses setuptools to define package metadata, entry points, and requirements.
"""

from setuptools import find_packages, setup

setup(
    name="cybercare",
    version="0.1.0",
    description="Cyber security event handling system",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "pyyaml",
        "psycopg2-binary",
        "python-dotenv",
        "requests",
    ],
    extras_require={
        "dev": [
            "types-PyYAML",
            "types-requests",
            "types-psycopg2",
            "mypy",
            "pytest",
            "pytest-asyncio",
            "black",
            "pylint",
        ]
    },
    entry_points={
        "console_scripts": [
            "cybercare-consumer=cybercare.consumer:main",
            "cybercare-propagator=cybercare.propagator:main",
        ],
    },
)
