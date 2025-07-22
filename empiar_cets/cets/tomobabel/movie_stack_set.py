from empiar_cets.yaml_parsing import ( 
    RegionDirective,  
)
from empiar_cets.empiar_utils import (
    EMPIARFileList, 
    get_files_matching_pattern, 
)

def  create_cets_tomobabel_movie_stack_set_from_region(
        region: RegionDirective, 
        empiar_files: EMPIARFileList, 
) -> dict:
    
    cets_movie_stack_set_dict = {}

    cets_movie_stacks = []
    for movie_stack in region.movie_stacks:
        # each movie stack dict correspond to a CETS MovieStack
        cets_movie_stack_dict = {}

        movie_stack_paths = get_files_matching_pattern(
            empiar_files, 
            movie_stack.file_pattern
        )

        # currently, should be one file per movie stack
        if len(movie_stack_paths) > 1:
            raise ValueError(f"Multiple files found matching pattern: {movie_stack.file_pattern}")

        if not movie_stack_paths:
            raise ValueError(f"No files found matching pattern: {movie_stack.file_pattern}")
        
        cets_movie_stack_dict = {"path": movie_stack_paths[0]}

        cets_tilt_series_movie_stack = {
            "frame_images": [cets_movie_stack_dict]
        }
        cets_movie_stacks.append(cets_tilt_series_movie_stack)

    cets_tilt_series = []
    if region.tilt_series:
        for tilt_series in region.tilt_series:
            # each tilt series dict correspond to a CETS TiltSeriesMicrograph
            cets_tilt_series_dict = {}

            tilt_series_paths = get_files_matching_pattern(
                empiar_files, 
                tilt_series.file_pattern
            )

            # currently, should be one file per movie stack
            if len(tilt_series_paths) > 1:
                raise ValueError(f"Multiple files found matching pattern: {tilt_series.file_pattern}")

            if not tilt_series_paths:
                raise ValueError(f"No files found matching pattern: {tilt_series_paths.file_pattern}")
            
            cets_tilt_series_dict = {"path": tilt_series_paths[0]}
        
            cets_tilt_series_micrograph_stack = {
                "micrographs": [cets_tilt_series_dict]
            }
            cets_tilt_series.append(cets_tilt_series_micrograph_stack)
    
    cets_movie_stack_set_dict["movie_stacks"] = cets_movie_stacks
    cets_movie_stack_set_dict["tilt_series"] = cets_tilt_series

    return cets_movie_stack_set_dict
