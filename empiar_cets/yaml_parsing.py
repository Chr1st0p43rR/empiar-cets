import re
from pathlib import Path
from ruamel.yaml import YAML
from typing import Optional, List
from pydantic import BaseModel


class Metadata(BaseModel):
    label: str
    file_pattern: str


class TiltSeries(BaseModel):
    label: str
    file_pattern: str


class MovieStack(BaseModel):
    label: str
    file_pattern: str
    metadata_label: Optional[str] = None


class RegionDirective(BaseModel):
    title: str
    metadata: Optional[List[Metadata]] = None
    movie_stacks: Optional[List[MovieStack]] = None    
    tilt_series: Optional[List[TiltSeries]] = None


def load_empiar_yaml_for_tomobabel(accession_id: str) -> dict:

    if not re.match(r'^EMPIAR-\d+$', accession_id):
        raise ValueError(f"Invalid EMPIAR accession ID format: {accession_id}")
    
    numeric_id = accession_id.split('-')[1]
    yaml_filename = f"empiar_{numeric_id}.yaml"
    yaml_fpath = Path("definition_files/tomobabel/")/yaml_filename
    
    yaml = YAML()
    try:
        with open(yaml_fpath) as fh:
            yaml_dict = yaml.load(fh)
            return yaml_dict
    except FileNotFoundError:
        raise FileNotFoundError(f"YAML file not found: {yaml_fpath}")
    except Exception as e:
        raise type(e)(f"Error parsing YAML file {yaml_fpath}: {str(e)}")
    

def load_empiar_yaml_for_czii(accession_id: str) -> dict:

    if not re.match(r'^EMPIAR-\d+$', accession_id):
        raise ValueError(f"Invalid EMPIAR accession ID format: {accession_id}")
    
    numeric_id = accession_id.split('-')[1]
    yaml_filename = f"empiar_{numeric_id}.yaml"
    yaml_fpath = Path("definition_files/czii/")/yaml_filename
    
    yaml = YAML()
    try:
        with open(yaml_fpath) as fh:
            yaml_dict = yaml.load(fh)
            return yaml_dict
    except FileNotFoundError:
        raise FileNotFoundError(f"YAML file not found: {yaml_fpath}")
    except Exception as e:
        raise type(e)(f"Error parsing YAML file {yaml_fpath}: {str(e)}")
    

def parse_regions(
        directive_dict: dict,
) -> list[RegionDirective]:
    
    regions = []
    for region in directive_dict["regions"]:
        region_directive = RegionDirective.model_validate(region)
        regions.append(region_directive)
    
    return regions



# def get_assigned_images_and_context(
#         study_uuid: str, 
#         dataset: Dataset, 
#         directive_dict: dict, 
# ) -> tuple[Optional[List[AssignedImage]], CreationContext]:

#     directives_by_title = {}
#     for dataset_conf in directive_dict['datasets']:
#         dataset_directive = DatasetDirectives.parse_obj(dataset_conf)
#         directives_by_title[dataset_directive.title] = dataset_directive

#     dataset_directive = directives_by_title[dataset.title]

#     assigned_images = dataset_directive.assigned_images
#     creation_context = CreationContext(
#         dataset=dataset,
#         object_lookup=instantiate_rembi_objects(directive_dict, study_uuid)
#     )

#     return assigned_images, creation_context
