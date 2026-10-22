# agentic-comm-automator/src/template_renderer.py
import os
import re
import string
from .utils import setup_logging

logger = setup_logging(__name__)

# Matches ${ENV_VAR_NAME} placeholders (upper-case names only, e.g. ${SENDER_EMAIL})
ENV_PATTERN = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)\}")


class TemplateRenderer:
    """
    A simple template renderer for string templates.
    1. ${ENV_VAR} placeholders are replaced with values from the environment (.env).
    2. {key} placeholders are filled from a context dictionary using Python's format syntax,
       so {sales_figure:.2f} and {attachments_meta[0][filepath]} also work.
    """
    def render(self, template_string, context):
        """Renders a template string using environment variables and a dictionary context."""
        if not template_string:
            return ""

        def replace_env(match):
            value = os.getenv(match.group(1))
            if value is None:
                raise ValueError(f"Environment variable '{match.group(1)}' used in template is not set.")
            return value

        try:
            text = ENV_PATTERN.sub(replace_env, template_string)
            return string.Formatter().vformat(text, [], context)
        except (KeyError, IndexError) as e:
            logger.error(f"Missing key in template context: {e}. Template: '{template_string}'")
            raise ValueError(f"Missing context key: {e}")
