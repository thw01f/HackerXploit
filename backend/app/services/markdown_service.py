import re
import yaml
import markdown
import bleach

def parse_markdown_frontmatter(content: str) -> tuple[dict, str]:
    """
    Parses YAML front-matter metadata at top of markdown string.
    Returns (meta_dict, body_markdown).
    """
    meta = {}
    body = content or ""

    pattern = r'^\s*---\s*\n(.*?)\n\s*---\s*\n(.*)$'
    match = re.match(pattern, content or "", re.DOTALL)
    if match:
        yaml_text, body = match.group(1), match.group(2)
        try:
            parsed = yaml.safe_load(yaml_text)
            if isinstance(parsed, dict):
                meta = {str(k).lower(): v for k, v in parsed.items()}
        except Exception:
            for line in yaml_text.splitlines():
                if ':' in line:
                    k, v = line.split(':', 1)
                    meta[k.strip().lower()] = v.strip().strip('"\'')

    return meta, body.strip()

ALLOWED_TAGS = [
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'p', 'br', 'strong', 'em', 'u', 's', 'blockquote',
    'ul', 'ol', 'li', 'code', 'pre', 'hr',
    'a', 'img', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'div', 'span'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title', 'width', 'height', 'class'],
    'code': ['class'],
    'pre': ['class'],
    'div': ['class'],
    'span': ['class']
}

def render_sanitized_html(markdown_text: str) -> str:
    """
    Renders markdown to HTML and strips dangerous XSS tags/attributes with bleach.
    """
    if not markdown_text:
        return ""

    html_raw = markdown.markdown(
        markdown_text,
        extensions=[
            'extra',
            'tables',
            'fenced_code'
        ]
    )

    sanitized = bleach.clean(
        html_raw,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        # 'data' deliberately excluded: bleach applies this allowlist to every
        # URL-bearing attribute it sanitizes (including <a href>, not just
        # <img src>), so allowing it would let authored content include a
        # data:text/html link that executes attacker HTML/script when a
        # reader clicks it - the sanitizer otherwise strips script tags and
        # inline event handlers, but a data: navigation sidesteps that.
        protocols=['http', 'https', 'mailto', 'blob', '']
    )

    return sanitized
