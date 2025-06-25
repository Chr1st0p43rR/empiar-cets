from typing import Any, Optional, Type
from pydantic import BaseModel, ValidationError
import rich


def dict_to_cets_model(
    dict: dict[str, Any],
    cets_model_class: Type[BaseModel],
) -> Optional[BaseModel]:
    
    cets_model = None
    try:
        cets_model = cets_model_class.model_validate(dict)
    except ValidationError:
        rich.print(
            f"[red]Validation error for {cets_model_class.__name__} with data: {dict}"
        )
    
    return cets_model
