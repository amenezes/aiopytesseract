from attrs import converters, field, frozen, validators


@frozen
class Parameter:
    name: str = field(validator=validators.instance_of(str))
    description: str = field(validator=validators.instance_of(str))
    value: str | None = field(
        default=None,
        converter=converters.default_if_none("-"),  # type: ignore
    )
