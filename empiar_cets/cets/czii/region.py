from empiar_cets.yaml_parsing import RegionDirective
from empiar_cets.empiar_utils import EMPIARFileList

from empiar_cets.cets.czii.movie_stack_collections import create_cets_czii_movie_stack_collection_from_region_directive
from empiar_cets.cets.czii.tilt_series import create_cets_czii_tilt_series_from_region_directive
from empiar_cets.cets.czii.alignment import create_cets_czii_alignment_from_region_directive
from empiar_cets.cets.czii.tomogram import create_cets_czii_tomograms_from_region_directive
from empiar_cets.metadata_parsing import load_mdoc_with_cache, load_xf_with_cache

def create_cets_czii_region_from_region_directive(
        accession_id: str,
        region: RegionDirective, 
        empiar_files: EMPIARFileList,
) -> dict:
    
    cets_region = {}

    movie_metadata = None
    if region.movie_metadata:
        movie_metadata = load_mdoc_with_cache(
            accession_id, 
            region.movie_metadata.file_pattern, 
            region.movie_metadata.label
        )
    
    if region.movie_stacks:
        cets_movie_stack_collection = create_cets_czii_movie_stack_collection_from_region_directive(
            accession_id, 
            region, 
            empiar_files, 
            movie_metadata
        )
        cets_region["movie_stack_collections"] = cets_movie_stack_collection
    
    if region.tilt_series_metadata:
        tilt_series_metadata = load_mdoc_with_cache(
            accession_id, 
            region.tilt_series_metadata.file_pattern, 
            region.tilt_series_metadata.label
        )

    if region.tilt_series:
        cets_tilt_series = create_cets_czii_tilt_series_from_region_directive(
            accession_id, 
            region, 
            empiar_files, 
            tilt_series_metadata)
        cets_region["tilt_series"] = cets_tilt_series

    if region.alignments:
        alignment_metadata = load_xf_with_cache(
            accession_id, 
            region.alignments.file_pattern, 
            region.alignments.label
        )
        cets_alignments = create_cets_czii_alignment_from_region_directive(alignment_metadata)
        cets_region["alignments"] = cets_alignments
    
    if region.tomograms:
        cets_tomograms = create_cets_czii_tomograms_from_region_directive(
            accession_id, 
            region, 
            empiar_files
        )
        cets_region["tomograms"] = cets_tomograms

    return cets_region


