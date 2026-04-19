from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import os

_env = Environment(
    loader=FileSystemLoader(
        os.path.join(os.path.dirname(__file__), "..", "templates")
    )
)


def render_template(template_name: str, **context) -> str:
    """Render a Jinja2 HTML template from the templates/ directory."""
    try:
        template = _env.get_template(template_name)
        return template.render(**context)
    except TemplateNotFound:
        raise ValueError(f"Template '{template_name}' not found.")
