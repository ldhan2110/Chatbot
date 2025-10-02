from dataclasses import dataclass, field
from datetime import datetime, timezone
from schema_ctx import fetch_schema_context, convert_schema_to_flat


@dataclass
class SqlDeps:
    engine: any
    schema_ctx: any = field(init=False)

    current_datetime: str = field(
        default_factory=lambda: datetime.now()
        .astimezone()
        .strftime("%B %d, %Y at %I:%M %p %Z")
    )

    def __post_init__(self):
        self.schema_ctx = convert_schema_to_flat(
            fetch_schema_context(self.engine, "C##PIDEV"))

    @property
    def today_date(self) -> str:
        return datetime.now(timezone.utc).date().isoformat()
