from typing import TypeAlias

Rate: TypeAlias = str  # e.g. '0.10', '0.12'
Threshold: TypeAlias = int
Year: TypeAlias = int
TaxBrackets: TypeAlias = dict[Year, dict[Rate, Threshold]]