from pathlib import Path
from pandas import DataFrame


def render_csv_document(
        dataframe: DataFrame,
        report_path: Path,
) -> None:

    try:
        dataframe.to_csv(report_path, index=False, encoding='utf-8')

    except FileNotFoundError:
        raise FileNotFoundError(f'По указанному пути {report_path} ничего не найдено!')


__all__ = [
    'render_csv_document',
]
