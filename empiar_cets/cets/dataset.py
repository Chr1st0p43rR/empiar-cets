from empiar_cets.models import Entry

def cets_dataset_from_entry(
        entry: Entry
) -> dict:
    
    cets_dataset = {}
    cets_dataset["name"] = entry.title

    return cets_dataset
