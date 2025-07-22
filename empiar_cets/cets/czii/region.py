import rich

from empiar_cets.yaml_parsing import RegionDirective
from empiar_cets.empiar_utils import EMPIARFileList

from empiar_cets.cets.czii.movie_stack_collections import create_cets_czii_movie_stack_collection_from_region
from empiar_cets.metadata_parsing import load_mdoc_with_cache

def create_cets_czii_region_from_region(
        accession_id: str,
        region: RegionDirective, 
        empiar_files: EMPIARFileList,
) -> dict:
    
    cets_region = {}

    metadata_file = None
    if region.metadata:
        metadata_file = load_mdoc_with_cache(
            accession_id, 
            region.metadata[0].file_pattern, 
            region.metadata[0].label
        )
    
    if region.movie_stacks:
        cets_movie_stack_collection = create_cets_czii_movie_stack_collection_from_region(region, empiar_files, metadata_file)
        cets_region["movie_stack_collections"] = cets_movie_stack_collection
    
    return cets_region


