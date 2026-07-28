import re
import html

def parse_markdown_frontmatter(content: str) -> tuple[dict, str]:
    """
    Parses YAML front-matter metadata at top of markdown string.
    Returns (meta_dict, body_markdown).
    """
    meta = {}
    body = content

    pattern = r'^\s*---\s*\n(.*?)\n\s*---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)
    if match:
        yaml_text, body = match.group(1), match.group(2)
        for line in yaml_text.splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                meta[k.strip().lower()] = v.strip().strip('"\'')

    return meta, body.strip()

def render_sanitized_html(markdown_text: str) -> str:
    """
    Renders markdown to HTML and strips dangerous XSS tags/attributes.
    """
    if not markdown_text:
        return ""

    # Pre-sanitize raw script/iframe tags and event handlers prior to rendering
    clean_text = re.sub(r'<script.*?>.*?</script>', '', markdown_text, flags=re.IGNORECASE | re.DOTALL)
    clean_text = re.sub(r'<iframe.*?>.*?</iframe>', '', clean_text, flags=re.IGNORECASE | re.DOTALL)
    clean_text = re.sub(r'on\w+\s*=\s*["\'].*?["\']', '', clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r'javascript:\s*', '', clean_text, flags=re.IGNORECASE)

    # Basic markdown parsing replacement for common tags
    rendered = html.escape(clean_text)

    # Unescape allowed markdown constructs
    rendered = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', rendered, flags=re.MULTILINE)
    rendered = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', rendered, flags=re.MULTILINE)
    rendered = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', rendered, flags=re.MULTILINE)
    rendered = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', rendered)
    rendered = re.sub(r'\*(.*?)\*', r'<em>\1</em>', rendered)
    rendered = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', rendered, flags=re.DOTALL)
    rendered = re.sub(r'`(.*?)`', r'<code>\1</code>', rendered)
    rendered = re.sub(r'^&gt; (.*?)$', r'<blockquote>\1</blockquote>', rendered, flags=re.MULTILINE)
    rendered = rendered.replace('\n\n', '<br/><br/>')

    # Post-check removal of escaped script/onload remnants
    sanitized = re.sub(r'&lt;script.*?&gt;.*?&lt;/script&gt;', '', rendered, flags=re.IGNORECASE | re.DOTALL)
    sanitized = re.sub(r'onload\s*=\s*.*?', '', sanitized, flags=re.IGNORECASE)

    return sanitized
