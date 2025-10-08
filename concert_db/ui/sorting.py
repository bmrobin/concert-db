from dataclasses import dataclass


@dataclass
class Sorting:
    column: int
    name: str
    ascending: bool | None = None


class SortableColumns:
    sort_asc = "↑"
    sort_desc = "↓"

    def __init__(self, column_names: list[str]) -> None:
        self.values: list[Sorting] = []
        for idx, name in enumerate(column_names):
            self.values.append(Sorting(idx, name=name, ascending=None))

    def __getitem__(self, index: int) -> Sorting:
        return self.values[index]

    def titles(self) -> list[str]:
        _titles = []
        for column in self.values:
            if column.ascending is not None:
                if bool(column.ascending):
                    _titles.append(f"{column.name} {self.sort_asc}")
                else:
                    _titles.append(f"{column.name} {self.sort_desc}")
            else:
                _titles.append(column.name)
        return _titles
