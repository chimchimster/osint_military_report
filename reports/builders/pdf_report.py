from pathlib import Path

from reports.utils.jinja_template import render_template
import pdfkit

path_to_css = Path('osint_military_report') / 'reports' / 'static' / 'css' / 'style.css'


def render_pdf_document(data: list[tuple], report_path: Path):
    config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
    _convert_process = pdfkit.from_string(
        render_template('pdf_template.html', data=data),
        str(report_path),
        configuration=config,
        options={"enable-local-file-access": "", "encoding": "UTF-8"},
        css=path_to_css
    )
    return 1 if _convert_process else 0


__all__ = [
    'render_pdf_document'
]
