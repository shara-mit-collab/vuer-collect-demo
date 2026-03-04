"""Small self-contained utilities used by collect_demo.py."""

import os
import xml.etree.ElementTree as ET
from contextlib import contextmanager
from pathlib import Path
from typing import Union


# ---------------------------------------------------------------------------
# Asset path extraction from MJCF XML
# ---------------------------------------------------------------------------

def collect_asset_paths(xml_path: Union[str, Path]) -> list[str]:
    """Parse an MJCF XML and return all referenced asset file paths."""
    try:
        tree = ET.parse(str(xml_path))
        root = tree.getroot()

        paths: set[str] = set()
        for asset in root.iter("asset"):
            for child in asset:
                fp = child.attrib.get("file")
                if fp:
                    paths.add(fp)
        return sorted(paths)

    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")
        return []
    except FileNotFoundError:
        print(f"File not found: {xml_path}")
        return []


# ---------------------------------------------------------------------------
# Working-directory context manager
# ---------------------------------------------------------------------------

@contextmanager
def WorkDir(new_directory):
    """Temporarily switch the current working directory."""
    original = os.getcwd()
    try:
        os.chdir(new_directory)
        yield
    finally:
        os.chdir(original)
