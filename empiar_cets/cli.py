import typer
import requests
import json
import logging
import rich

from tomobabel.models.top_level import DataSet

from .models import Entry
from .cets_object_utils import dict_to_cets_model
from .cets.dataset import cets_dataset_from_entry

logger = logging.getLogger("empiar_cets.cli")


app = typer.Typer()


def empiar_entry_from_accession_id(accession_id: str) -> Entry:
    accession_no = accession_id.split("-")[1]
    logger.info(f"Generating study for EMPIAR entry {accession_no}")
    empiar_uri = f"https://www.ebi.ac.uk/empiar/api/entry/{accession_no}"

    r = requests.get(empiar_uri)
    raw_data = json.loads(r.content)

    accession_obj = raw_data[accession_id]
    entry = Entry.model_validate(accession_obj)

    return entry


@app.command()
def make_dataset(accession_id: str):
    """
    Create a dataset from an EMPIAR accession ID.
    """

    entry = empiar_entry_from_accession_id(accession_id)
    cets_dataset_dict = cets_dataset_from_entry(entry)
    rich.print(f"[green]CETS Dataset created for {accession_id}:[/green]")
    cets_dataset = dict_to_cets_model(
        cets_dataset_dict, cets_model_class=DataSet
    )
    rich.print(cets_dataset)
    


@app.command()
def dummy_func():
    pass