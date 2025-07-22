from empiar_cets.models import Entry

def start_cets_tomobabel_dataset_from_empiar_entry(
        entry: Entry
) -> dict:
    
    cets_dataset = {}
    cets_dataset["name"] = entry.title

    return cets_dataset
