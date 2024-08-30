from typing import Annotated, Any, Dict, List
from pydantic import BaseModel, BeforeValidator
from pydantic_core import core_schema


class GroupPermissionDict(Dict[str, bool]):
    _permissions = {
        "read": False,
        "write": False,
        "delete": False,
        "invite_user": False,
        "invite_to_group": False,
        "manage_groups": False,
        "manage_storage_entity": False,
    }

    def __init__(self):
        super().__init__(self._permissions)
        self.__dict__ = self   

    def __setitem__(self, key, value):
        if key not in self:
            raise KeyError(f"Key '{key}' is not allowed. Available keys are: {list(self.keys())}")
        if not isinstance(value, bool):
            raise ValueError("Value must be a boolean")
        super().__setitem__(key, value)
    
    def __delitem__(self, key):
        if key in self:
            raise KeyError(f"Cannot delete key '{key}'")
        raise KeyError(f"Key '{key}' does not exist")

    def __repr__(self):
        return f"{self.__class__.__name__}({super().__repr__()})"
    
    def set_item(
            self,
            key: str,
            value: bool = False,
    ):
        if key not in self:
            raise KeyError(f"Key '{key}' is not allowed. Available keys are: {list(self.keys())}")
        
        super().__setitem__(key, value)      

    @classmethod
    def validate(cls, field_value: Any) -> Dict[str, bool]:
        if isinstance(field_value, dict):
            for key, value in field_value.items():
                if not isinstance(key, str):
                    raise ValueError(f"Key '{key}' is not a string")
                if not isinstance(value, bool):
                    raise ValueError(f"Value '{value}' for key '{key}' is not a boolean")
            return field_value
        raise ValueError(f"Field value is not a dictionary, it is a {type(field_value)} ")

    @classmethod
    def __get_pydantic_core_schema__(cls, source: Any, handler) -> Any:
        return core_schema.with_info_before_validator_function(
            cls.validate, handler(Dict[str, bool]), field_name=handler.field_name
        )


class StorageEntityGroup(BaseModel):
    name: str
    permissions: Annotated[Dict[str, bool], BeforeValidator(GroupPermissionDict.validate)]


class StorageEntityGroupList(List[StorageEntityGroup]):
    perms = GroupPermissionDict()
    perms["read"] = True
    _observer_group = StorageEntityGroup(
        name="observer",
        permissions=perms,
    )

    def __init__(self):
        super().__init__([self._observer_group])

    def append(self, item):
        if not isinstance(item, StorageEntityGroup):
            raise TypeError("All elements must be strings")
        super().append(item)
    
    def insert(self, index, item):
        if not isinstance(item, StorageEntityGroup):
            raise TypeError("All elements must be strings")
        super().insert(index, item)
    
    def extend(self, iterable):
        if not all(isinstance(item, StorageEntityGroup) for item in iterable):
            raise TypeError("All elements must be strings")
        super().extend(iterable)
    
    def remove(self, item):
        if item == self._observer_group:
            raise ValueError(f"Cannot remove the persistent element '{self._observer_group}'")
        super().remove(item)
    
    def pop(self, index=-1):
        if self[index] == self._observer_group:
            raise ValueError(f"Cannot remove the persistent element '{self._observer_group}'")
        return super().pop(index)
    
    def __repr__(self):
        return f"{self.__class__.__name__}({super().__repr__()})"
    
    # TODO: написать какую-нибудь проверку
    @classmethod
    def validate(cls, field_value: Any) -> List[StorageEntityGroup]:
        return field_value

    @classmethod
    def __get_pydantic_core_schema__(cls, source: Any, handler) -> Any:
        return core_schema.with_info_before_validator_function(
            cls.validate, handler(List[StorageEntityGroup]), field_name=handler.field_name
        )
    


# if __name__ == "__main__":
#     l = StorageEntityGroupList()
#     print(l[0])