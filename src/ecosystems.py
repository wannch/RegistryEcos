from enum import Enum, IntEnum
from typing import Any

class ECOSYSTEM(IntEnum):
    PYPI = 0
    NPM = 1
    GO = 2

    def __reduce_ex__(self, protocol) -> tuple[Any, ...]:
        return (self.__class__, (self.value,))

def get_friendly_name(ecosystem: ECOSYSTEM) -> str:
    match ecosystem:
        case ECOSYSTEM.PYPI:
            return "PyPI"
        case ECOSYSTEM.NPM:
            return "npm"
        case ECOSYSTEM.GO:
            return "go"
        case _:
            return ecosystem.value

if __name__ == '__main__':
    enum_obj = ECOSYSTEM.GO
    import pickle
    pickled_data = pickle.dumps(enum_obj)
    print(pickled_data)