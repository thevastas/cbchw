"""
Shared utility functions for the Cybercare package.

This module provides common functionality used across different
components of the Cybercare package, such as configuration loading
and command-line argument parsing.
"""

import argparse
import logging
import os
import string
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv


def load_config(config_path: str) -> Dict[str, Any]:
    """Load and process configuration from a YAML file.

    This function reads a YAML configuration file and replaces any environment
    variables (in the format ${VAR_NAME}) with their actual values.

    Args:
        config_path (str): Path to the configuration file

    Returns:
        Dict[str, Any]: The loaded configuration as a dictionary,
                        or an empty dict if loading fails
    """
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config_content = f.read()

        template = string.Template(config_content)
        config_content = template.safe_substitute(os.environ)

        return yaml.safe_load(config_content)
    except FileNotFoundError:
        logging.error("Configuration file not found: %s", config_path)
        return {}
    except PermissionError:
        logging.error("Permission denied when accessing config file: %s", config_path)
        return {}
    except yaml.YAMLError as e:
        logging.error("Invalid YAML in config file %s: %s", config_path, e)
        return {}
    except Exception as e:  # pylint: disable=broad-exception-caught
        logging.error("Unexpected error loading config from %s: %s", config_path, e)
        return {}


def setup_basic_app(
    app_name: str, section_name: Optional[str] = None
) -> Dict[str, Any]:
    """Set up basic application configuration.

    This function initializes logging, loads environment variables,
    parses command line arguments, and loads the configuration from
    the specified section of the configuration file.

    Args:
        app_name (str): Name of the application
        section_name (Optional[str]): Section name in the config file (if None, returns the entire config)

    Returns:
        Dict[str, Any]: The loaded configuration section
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    load_dotenv()

    parser = argparse.ArgumentParser(description=f"{app_name} Service")
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to the configuration file (default: config.yaml)",
    )
    args = parser.parse_args()

    config = load_config(args.config)

    if not config:
        logging.error("Configuration is empty or invalid.")
        return {}

    # Return the specific section if requested, otherwise return the entire config
    if section_name and section_name in config:
        return config[section_name]

    return config
