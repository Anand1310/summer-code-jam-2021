from typing import Any, Iterator, List, Optional, Tuple, TypeVar

T = TypeVar("T")


def transpose(*rows: List[T]) -> Iterator[T]:
    """Transpose a list of rows into a list of columns or vice-versa."""
    return map(list, zip(*rows))


def row_with_separators(separators: Tuple[str, str, str], row: Tuple[str, ...]) -> str:
    """Return row with separators."""
    left, middle, right = separators
    return f"{left}{middle.join(map(str, row))}{right}"


def make_table(
    rows: List[List[Any]], labels: Optional[List[Any]] = None, centered: bool = False
) -> str:
    """Make table.

    :param rows: 2D array containing object that can be converted to string using `str(obj)`.
    :param labels: Array containing the column labels, the length must equal that of rows.
    :param centered: If the items should be aligned to the center, else they are left aligned.
    :return: A table representing the rows passed in.
    """
    # Transpose into columns
    columns = list(transpose(labels, *rows) if labels else transpose(*rows))

    # Padding
    for column in columns:
        # Find the required column width
        column_width = max(map(len, map(str, column)))

        # Add and record padding
        for i, item in enumerate(column):
            column[i] = (
                f" {str(item):^{column_width}} "
                if centered
                else f" {str(item):<{column_width}} "
            )

    # Border Widths
    horizontal_lines = tuple("─" * len(column[0]) for column in columns)

    # Create a list of rows with the row separators
    rows = [row_with_separators(("│", "│", "│"), row) for row in transpose(*columns)]

    # Create a separator between the labels and the values if needed
    if labels:
        label_border_bottom = row_with_separators(("├", "┼", "┤"), horizontal_lines)
        rows.insert(1, label_border_bottom)

    # Create the top and bottom border of the table
    top_border = row_with_separators(("┌", "┬", "┐"), horizontal_lines)
    rows.insert(0, top_border)

    bottom_border = row_with_separators(("└", "┴", "┘"), horizontal_lines)
    rows.append(bottom_border)

    # Join all the components
    return "\n".join(rows)
