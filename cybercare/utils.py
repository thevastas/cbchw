"""
Shared utility functions for the Cybercare package.

This module provides common functionality used across different
components of the Cybercare package, such as configuration loading
and command-line argument parsing.
"""

import argparse
import logging
import os
import re
from typing import Any, Dict

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
        if not os.path.exists(config_path):
            logging.error("Configuration file not found: %s", config_path)
            return {}

        with open(config_path, "r", encoding="utf-8") as f:
            config_content = f.read()

        # Replace environment variables in a single pass
        config_content = re.sub(
            r"\${([^}]+)}",
            lambda m: os.environ.get(m.group(1), f"${{{m.group(1)}}}"),
            config_content,
        )

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


def setup_basic_app(app_name: str, default_config_path: str) -> Dict[str, Any]:
    """Set up basic application configuration.

    This function initializes logging, loads environment variables,
    parses command line arguments, and loads the configuration file.

    Args:
        app_name (str): Name of the application
        default_config_path (str): Default path to the configuration file

    Returns:
        Dict[str, Any]: The loaded configuration
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
        default=default_config_path,
        help=f"Path to the configuration file (default: {default_config_path})",
    )
    args = parser.parse_args()

    config = load_config(args.config)

    if not config:
        logging.error("Configuration is empty or invalid.")

    return config
