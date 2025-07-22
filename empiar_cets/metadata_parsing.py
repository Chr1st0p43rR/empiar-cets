import re
import json
import os
import tempfile
import urllib.request
from typing import List, Optional, Union
from pathlib import Path

from .metadata_models import MdocFile, ZValueSection


def download_mdoc_from_empiar(url: str) -> str:

    suffix = '.mdoc'
    temp_fd, local_path = tempfile.mkstemp(suffix=suffix, prefix='mdoc_')
    os.close(temp_fd)
    
    try:
        print(f"Downloading {url}...")
        urllib.request.urlretrieve(url, local_path)
        print(f"Downloaded to {local_path}")
        return local_path
    except Exception as e:
        raise Exception(f"Failed to download {url}: {str(e)}")


def save_mdoc_to_json(mdoc: MdocFile, filepath: str) -> None:
    
    with open(filepath, 'w') as f:
        json.dump(mdoc.to_dict(), f, indent=2)


def load_mdoc_from_json(filepath: str) -> MdocFile:
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    return MdocFile.from_dict(data)


def load_mdoc_with_cache(
        accession_id: str, 
        file_pattern: str,
        mdoc_label: str,
) -> MdocFile:
    
    accession_no = accession_id.split("-")[1]

    url_base = "https://ftp.ebi.ac.uk/empiar/world_availability/" 
    url = f"{url_base}{accession_no}/data/{file_pattern}"

    cache_dirpath = Path(f"local-data/{accession_id}/cache/mdoc/{mdoc_label}")
    cache_dirpath.mkdir(exist_ok=True, parents=True)
    cache_path = cache_dirpath / f"{mdoc_label}.json"
    
    if Path(cache_path).exists():
        return load_mdoc_from_json(cache_path)
    
    temp_mdoc_path = download_mdoc_from_empiar(url)
    
    try:
        print(f"Parsing {temp_mdoc_path}...")
        mdoc = parse_mdoc_file(temp_mdoc_path)
        
        print(f"Caching to {cache_path}...")
        save_mdoc_to_json(mdoc, cache_path)
        
        return mdoc
        
    finally:
        Path(temp_mdoc_path).unlink()


def clear_cache(cache_dir: str = "mdoc_cache") -> None:
    """Remove all cached files"""
    cache_path = Path(cache_dir)
    if cache_path.exists():
        for file in cache_path.glob("*.json"):
            file.unlink()
        print(f"Cleared cache directory: {cache_dir}")


def list_cached_files(cache_dir: str = "mdoc_cache") -> List[str]:
    """List all cached JSON files"""
    cache_path = Path(cache_dir)
    if not cache_path.exists():
        return []
    
    return [str(f) for f in cache_path.glob("*.json")]


def parse_value(value_str: str) -> Union[str, int, float]:
    """
    Parse a string value to appropriate type (int, float, or str)
    """
    value_str = value_str.strip()
    
    # Try integer first
    try:
        return int(value_str)
    except ValueError:
        pass
    
    # Try float
    try:
        return float(value_str)
    except ValueError:
        pass
    
    # Return as string
    return value_str


def parse_mdoc_file(filepath: str) -> MdocFile:
    """
    Parse an .mdoc file and return a MdocFile object
    
    Args:
        filepath: Path to the .mdoc file
        
    Returns:
        MdocFile object containing parsed data
    """
    mdoc = MdocFile(filename=str(filepath))
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    current_section = None
    in_global_headers = True
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Handle comments (lines starting with [T = )
        if line.startswith('[T =') and line.endswith(']'):
            comment = line[4:-1].strip()  # Remove [T = and ]
            mdoc.comments.append(comment)
            continue
        
        # Handle ZValue sections
        z_value_match = re.match(r'\[ZValue\s*=\s*(\d+)\]', line)
        if z_value_match:
            z_value = int(z_value_match.group(1))
            current_section = ZValueSection(z_value=z_value)
            mdoc.z_sections.append(current_section)
            in_global_headers = False
            continue
        
        # Handle key-value pairs
        if '=' in line and not line.startswith('['):
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            # Parse value to appropriate type
            parsed_value = parse_value(value)
            
            # Add to appropriate section
            if in_global_headers:
                mdoc.global_headers[key] = parsed_value
            elif current_section is not None:
                current_section[key] = parsed_value
    
    return mdoc
