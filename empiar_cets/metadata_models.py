from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class ZValueSection:
    """Represents a single [ZValue = n] section from an .mdoc file"""
    z_value: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access to metadata"""
        return self.metadata.get(key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Allow dictionary-style setting of metadata"""
        self.metadata[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get metadata value with optional default"""
        return self.metadata.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ZValueSection to dictionary for JSON serialization"""
        return {
            'z_value': self.z_value,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ZValueSection':
        """Create ZValueSection from dictionary (for JSON deserialization)"""
        section = cls(z_value=data['z_value'])
        section.metadata = data['metadata']
        return section


@dataclass
class MdocFile:
    """Represents a parsed .mdoc file with global headers and ZValue sections"""
    filename: Optional[str] = None
    global_headers: Dict[str, Any] = field(default_factory=dict)
    z_sections: List[ZValueSection] = field(default_factory=list)
    comments: List[str] = field(default_factory=list)
    
    def __len__(self) -> int:
        """Return number of Z sections"""
        return len(self.z_sections)
    
    def __getitem__(self, index: int) -> ZValueSection:
        """Allow indexing into Z sections"""
        return self.z_sections[index]
    
    def get_section_by_z_value(self, z_value: int) -> Optional[ZValueSection]:
        """Get a section by its Z value"""
        for section in self.z_sections:
            if section.z_value == z_value:
                return section
        return None
    
    def search_by_subframe_path(self, search_string: str, case_sensitive: bool = False) -> List[ZValueSection]:
        """
        Search for sections where the SubFramePath ends with the given search string.
        
        Args:
            search_string: String to match against the end of SubFramePath
            case_sensitive: Whether to perform case-sensitive matching
            
        Returns:
            List of ZValueSection objects that match the criteria
        """
        matches = []
        
        for section in self.z_sections:
            subframe_path = section.get('SubFramePath', '')
            if not subframe_path:
                continue
                
            # Convert to string if not already
            subframe_path = str(subframe_path)
            
            # Perform case-insensitive comparison if requested
            if not case_sensitive:
                subframe_path = subframe_path.lower()
                search_string = search_string.lower()
            
            # Check if the path ends with the search string
            if subframe_path.endswith(search_string):
                matches.append(section)
        
        return matches
    
    def get_tilt_angles(self) -> List[float]:
        """Get all tilt angles from the Z sections"""
        angles = []
        for section in self.z_sections:
            angle = section.get('TiltAngle')
            if angle is not None:
                angles.append(float(angle))
        return angles
    
    def get_subframe_paths(self) -> List[str]:
        """Get all SubFramePath values"""
        paths = []
        for section in self.z_sections:
            path = section.get('SubFramePath')
            if path:
                paths.append(str(path))
        return paths
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert MdocFile to dictionary for JSON serialization"""
        return {
            'filename': self.filename,
            'global_headers': self.global_headers,
            'z_sections': [section.to_dict() for section in self.z_sections],
            'comments': self.comments
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MdocFile':
        """Create MdocFile from dictionary (for JSON deserialization)"""
        mdoc = cls(
            filename=data.get('filename'),
            global_headers=data.get('global_headers', {}),
            comments=data.get('comments', [])
        )
        mdoc.z_sections = [
            ZValueSection.from_dict(section_data) 
            for section_data in data.get('z_sections', [])
        ]
        return mdoc

