import os
import importlib
from fastapi import APIRouter

router = APIRouter(prefix="/v1")

directory = os.path.dirname(__file__)

for filename in os.listdir(directory):
    if (
        filename.endswith(".py")
        and filename != "__init__.py"
        and not filename.startswith(".")
    ):
        module_name = filename[:-3]
        try:
            module = importlib.import_module(f".{module_name}", package=__name__)
        except ImportError as e:
            print(f"Error importing module {module_name}: {e}")
            continue
        
        router_to_include = getattr(module, "router", None)
        if isinstance(router_to_include, APIRouter):
            router.include_router(router_to_include)