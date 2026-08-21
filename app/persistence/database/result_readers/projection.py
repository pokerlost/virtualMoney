"""Validated projection extraction from SQLAlchemy mapping results."""

from __future__ import annotations

from pydantic import TypeAdapter
from sqlalchemy.engine import MappingResult, Result

from persistence.projections import ProjectionModel


class SQLAlchemyProjectionResultReader[ProjectionT: ProjectionModel]:
    """Materialize labeled mapping rows as one Pydantic projection type."""

    def __init__[*RowT](
        self,
        result: Result[tuple[*RowT]],
        projection_type: type[ProjectionT],
    ) -> None:
        """Wrap mapping rows and their validated projection type."""
        self._result: MappingResult = result.mappings()
        self._adapter = TypeAdapter(projection_type)

    def one(self) -> ProjectionT:
        """Validate and return exactly one projection row."""
        return self._adapter.validate_python(self._result.one())

    def one_or_none(self) -> ProjectionT | None:
        """Validate and return zero or one projection row."""
        row = self._result.one_or_none()
        return None if row is None else self._adapter.validate_python(row)

    def all(self) -> list[ProjectionT]:
        """Validate and materialize every projection row in result order."""
        return [self._adapter.validate_python(row) for row in self._result.all()]
