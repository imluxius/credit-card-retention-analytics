"""Generate a portable dashboard: no server, CDN, tracking, or JS dependencies."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def build_dashboard(result: dict, destination: Path) -> None:
    template = (ROOT / 'dashboard/template.html').read_text(encoding='utf-8')
    # JSON is placed inside a script element; escape HTML delimiters defensively.
    payload = json.dumps(result['dashboard_rows'], separators=(',', ':')).replace('<', '\\u003c')
    html = template.replace('__CUSTOMER_DATA__', payload)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html, encoding='utf-8')
