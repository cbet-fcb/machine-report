from pydantic import BaseModel, Field

class UnitFinder:
    index: int = Field(default=-1, description="Unit needed to be found")
    pass