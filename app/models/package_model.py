from bson import ObjectId

from pydantic import BaseModel, Field

from datetime import datetime


class PackageModel(BaseModel):
    name: str = Field(...)
    moment: datetime = Field(...)
    versions: list[ObjectId] | None = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            'example': {
                'name': 'urllib3',
                'moment': datetime.now(),
                'versions': []
            }
        }