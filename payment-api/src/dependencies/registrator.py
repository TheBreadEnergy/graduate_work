from typing import Callable, Type

dependencies: dict[Type | Callable, Callable] = {}


def add_factory_to_mapper(class_: Type | Callable):
    def _add_factory_to_mapper(factory: Callable):
        dependencies[class_] = factory
        return factory

    return _add_factory_to_mapper
