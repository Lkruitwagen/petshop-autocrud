from typing import Union, Dict, Any, List
from datetime import datetime

from sqlmodel import SQLModel

serializers = {
    datetime: lambda x: x.isoformat()
}

def root(includes: List[str]):
    return [el.split('.')[0] for el in includes]

def strip(includes: List[str], base:str):
    return [ob.replace(base + ".", "") for ob in includes if base in ob]

class IncludesSerializer:

    # inspired by https://github.com/tiangolo/sqlmodel/issues/444

    def __init__(
        self,
        serializers: Union[Dict[Any,Any], None]=None
    ):
        
        self.serializers = serializers if serializers else {}

    def _serialize(self, field:Any) -> str:
        serializer = self.serializers.get(type(field))
        if not serializer:
            raise Exception("No matching serializer found for data.")
        serialized_data = serializer(field)
        if not isinstance(serialized_data, str):
            raise Exception("Serializer not converting to string.")
        return serialized_data


    def __call__(
            self, 
            models: Union[List[SQLModel],SQLModel],
            parent: Union[List,Dict],
            includes: List[str],
        ) -> Union[List,Dict]:

        if isinstance(models, List) and isinstance(parent, List):
            parent.extend([self(obj, {}, includes) for obj in models])
            return parent
        
    
        # handle single objects, 
        for key in list(models.model_fields.keys()) + list(models.__sqlmodel_relationships__.keys()):
            if (
                ("_sa_instance_state" not in key) and
                ((key in models.model_fields.keys()) or (key in root(includes)))
            ):
                attr = getattr(models, key)
                if isinstance(attr, List):
                    attr = [self(obj, {}, strip(includes,key) if key in models.__sqlmodel_relationships__.keys() else includes) for obj in attr] # trim includes here
                if isinstance(attr, SQLModel):
                    attr = self(attr, {}, strip(includes,key) if key in models.__sqlmodel_relationships__.keys() else includes) # trim includes
                if isinstance(attr, tuple(self.serializers.keys())):
                    attr = self._serialize(attr)
                if not isinstance(parent, Dict):
                    raise Exception("Walk error (parent is not a dict).")
                
                # no serializer defined - pass open
                parent[key] = attr

        return parent
    

includes_serializer = IncludesSerializer(serializers)