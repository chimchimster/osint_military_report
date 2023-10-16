from pathlib import Path
from pandas import DataFrame, ExcelWriter


def render_xlsx_document(
        dataframe: DataFrame,
        report_path: Path,
        sheet_name: str,
) -> None:

    try:
        with ExcelWriter(report_path, engine='xlsxwriter', mode='w') as writer:
            dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
            for column in dataframe:
                column_width = max(dataframe[column].astype(str).map(len).max(), len(column)) + 1
                col_idx = dataframe.columns.get_loc(column)
                writer.sheets[sheet_name].set_column(col_idx, col_idx, column_width)

    except FileNotFoundError:
        raise FileNotFoundError(f'По указанному пути {report_path} ничего не найдено!')


__all__ = [
    'render_xlsx_document',
]
