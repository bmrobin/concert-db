from concert_db.ui.shared import Columns


def test_columns_initialization() -> None:
    cols = Columns(["A", "B", "C"])
    assert len(cols.values) == 3
    assert cols[0].name == "A"
    assert cols[0].ascending is None
    assert cols[1].name == "B"
    assert cols[1].ascending is None
    assert cols[2].name == "C"
    assert cols[2].ascending is None


def test_columns_titles_sorting() -> None:
    cols = Columns(["A", "B", "C"])

    # default has no sorting
    assert cols.titles() == ["A", "B", "C"]

    # verify asc/desc on each column
    cols[0].ascending = True
    assert cols.titles() == ["A ↑", "B", "C"]
    cols[0].ascending = False
    assert cols.titles() == ["A ↓", "B", "C"]
    cols[0].ascending = None

    cols[1].ascending = True
    assert cols.titles() == ["A", "B ↑", "C"]
    cols[1].ascending = False
    assert cols.titles() == ["A", "B ↓", "C"]
    cols[1].ascending = None

    cols[2].ascending = True
    assert cols.titles() == ["A", "B", "C ↑"]
    cols[2].ascending = False
    assert cols.titles() == ["A", "B", "C ↓"]
