from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


template_env = Environment(loader=FileSystemLoader(
        Path('osint_military_report') / 'reports' / 'templates'
    ),
    autoescape=select_autoescape(['html']),
)


def render_template(template_name: str, **context) -> str:

    template = template_env.get_template(template_name)
    html = template.render(context)

    return html
