import tomobabel.models.top_level
import typer
import requests
import json
import logging
import rich

import tomobabel.models
import cryoet_metadata._base._models

from .models import Entry
from .cets_object_utils import dict_to_cets_model, save_cets_model_to_json
from .empiar_utils import get_files_for_empiar_entry_cached
from .yaml_parsing import (
    load_empiar_yaml_for_tomobabel, 
    load_empiar_yaml_for_czii, 
    parse_regions
)

from .cets.tomobabel.dataset import start_cets_tomobabel_dataset_from_empiar_entry
from .cets.tomobabel.movie_stack_set import create_cets_tomobabel_movie_stack_set_from_region

from .cets.czii.region import create_cets_czii_region_from_region_directive


logger = logging.getLogger("empiar_cets.cli")


app = typer.Typer()


def empiar_entry_from_accession_id(accession_id: str) -> Entry:

    accession_no = accession_id.split("-")[1]
    empiar_uri = f"https://www.ebi.ac.uk/empiar/api/entry/{accession_no}"

    r = requests.get(empiar_uri)
    raw_data = json.loads(r.content)

    accession_obj = raw_data[accession_id]
    entry = Entry.model_validate(accession_obj)

    return entry


@app.command()
def convert_empiar_to_cets(
    accession_id: str, 
    cets_implementation: str = "czii"
):
    
    entry = empiar_entry_from_accession_id(accession_id)
    rich.print(f"[green]Got EMPIAR Entry for {accession_id}:[/green]")

    if cets_implementation == "tomobabel":

        # make_dataset
        cets_dataset_dict = start_cets_tomobabel_dataset_from_empiar_entry(entry)
        cets_dataset = dict_to_cets_model(
            cets_dataset_dict, cets_model_class=tomobabel.models.top_level.DataSet
        )
        rich.print(f"[green]CETS Dataset created for {accession_id}:[/green]")
        rich.print(cets_dataset)

        # process_regions
        directive_dict = load_empiar_yaml_for_tomobabel(accession_id)
        rich.print(f"[green]Loaded YAML for {accession_id}:[/green]")

        regions = parse_regions(directive_dict)
        rich.print(f"[green]Processed regions for {accession_id}:[/green]")
        rich.print(regions)

        # get_empiar_files
        empiar_files = get_files_for_empiar_entry_cached(accession_id)
        rich.print(f"[green]Got {len(empiar_files.files)} files for {accession_id}:[/green]")

        # make movie stack sets (in tomo image sets)
        cets_regions = {}
        for region in regions:
            if region.movie_stacks:
                movie_stack_set = create_cets_tomobabel_movie_stack_set_from_region(region, empiar_files)
                cets_regions[region.title] = movie_stack_set

                cets_movie_stack_set = dict_to_cets_model(
                    movie_stack_set, cets_model_class=tomobabel.models.top_level.MovieStackSet
                )
                rich.print(f"[green]CETS MovieStackSet created for {accession_id}:[/green]")
                rich.print(cets_movie_stack_set)
        
        rich.print(f"[green]cets_regions: {cets_regions}[/green]")
    
    elif cets_implementation == "czii":
        
        directive_dict = load_empiar_yaml_for_czii(accession_id)
        regions = parse_regions(directive_dict)

        empiar_files = get_files_for_empiar_entry_cached(accession_id)

        cets_dataset_dict = {}
        dataset_regions = []
        for region in regions:
            cets_region_dict = create_cets_czii_region_from_region_directive(
                accession_id,
                region, 
                empiar_files
            )
            dataset_regions.append(cets_region_dict)

        cets_dataset_dict["name"] = accession_id
        cets_dataset_dict["regions"] = dataset_regions
        cets_dataset = dict_to_cets_model(
            cets_dataset_dict, 
            cets_model_class=cryoet_metadata._base._models.Dataset
        )
        save_cets_model_to_json(accession_id, accession_id, cets_dataset)      


@app.command()
def dummy():
    pass
