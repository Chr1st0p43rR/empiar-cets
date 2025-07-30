import re
import json
import os
import tempfile
import urllib.request
from typing import List, Optional, Union, Dict, Any
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


def download_xf_from_empiar(url: str) -> str:
    """Download .xf file from EMPIAR"""
    suffix = '.xf'
    temp_fd, local_path = tempfile.mkstemp(suffix=suffix, prefix='xf_')
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


def save_alignment_to_json(alignment: Dict[str, Any], filepath: str) -> None:
    """Save Alignment object to JSON file"""
    with open(filepath, 'w') as f:
        json.dump(alignment, f, indent=2)


def load_mdoc_from_json(filepath: str) -> MdocFile:
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    return MdocFile.from_dict(data)


def load_alignment_from_json(filepath: str) -> Dict[str, Any]:
    """Load Alignment object from JSON file"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    return data


def load_mdoc_with_cache(
        accession_id: str, 
        file_pattern: str,
        mdoc_label: str,
) -> MdocFile:
    
    accession_no = accession_id.split("-")[1]

    url_base = "https://ftp.ebi.ac.uk/empiar/world_availability/" 
    url = f"{url_base}{accession_no}/data/{file_pattern}"

    cache_dirpath = Path(f"local-data/{accession_id}/mdoc")
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


def load_xf_with_cache(
        accession_id: str, 
        file_pattern: str,
        xf_label: str,
) -> Dict[str, Any]:
    
    accession_no = accession_id.split("-")[1]

    url_base = "https://ftp.ebi.ac.uk/empiar/world_availability/" 
    url = f"{url_base}{accession_no}/data/{file_pattern}"

    cache_dirpath = Path(f"local-data/{accession_id}/xf")
    cache_dirpath.mkdir(exist_ok=True, parents=True)
    cache_path = cache_dirpath / f"{xf_label}.json"
    
    if Path(cache_path).exists():
        return load_alignment_from_json(cache_path)
    
    temp_xf_path = download_xf_from_empiar(url)
    
    try:
        print(f"Parsing {temp_xf_path}...")
        alignment = parse_xf_file(temp_xf_path)
        
        print(f"Caching to {cache_path}...")
        save_alignment_to_json(alignment, cache_path)
        
        return alignment
        
    finally:
        Path(temp_xf_path).unlink()


def clear_cache(cache_dir: str = "mdoc_cache") -> None:
    """Remove all cached files"""
    cache_path = Path(cache_dir)
    if cache_path.exists():
        for file in cache_path.glob("*.json"):
            file.unlink()
        print(f"Cleared cache directory: {cache_dir}")


def clear_xf_cache(accession_id: str) -> None:
    """Remove all cached .xf files for a specific accession"""
    cache_path = Path(f"local-data/{accession_id}/cache/xf")
    if cache_path.exists():
        for file in cache_path.glob("*.json"):
            file.unlink()
        print(f"Cleared XF cache directory: {cache_path}")


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


def parse_xf_file(
    filepath: str, 
) -> Dict[str, Any]:
    
    projection_alignments = []
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Parse the six values: a11 a12 a21 a22 dx dy
        values = line.split()
        if len(values) != 6:
            print(f"Warning: Line {i+1} has {len(values)} values instead of 6, skipping")
            continue
        
        try:
            a11, a12, a21, a22, dx, dy = [float(v) for v in values]
        except ValueError as e:
            print(f"Warning: Could not parse line {i+1}: {line}, error: {e}")
            continue
        
        # Create the transformation sequence
        # Option 1: Separate Affine (rotation) and Translation
        affine_transform = {
            "type": "affine",
            "name": f"rotation_projection_{i}",
            "output": f"rotated_projection_{i}",
            "affine": [
                [a11, a12, 0.0],
                [a21, a22, 0.0],
                [0.0, 0.0, 1.0]
            ]
        }
        
        translation_transform = {
            "type": "translation",
            "name": f"translation_projection_{i}",
            "input": f"rotated_projection_{i}",
            "translation": [dx, dy]
        }
        
        # Create ProjectionAlignment
        projection_alignment = {
            "type": "sequence",
            "name": f"alignment_projection_{i}",
            "sequence": [affine_transform, translation_transform]
        }
        
        projection_alignments.append(projection_alignment)
    
    # Create the main Alignment object
    alignment = {
        "projection_alignments": projection_alignments
    }
    
    return alignment


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