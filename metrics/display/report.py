"""Self-contained, printable HTML tables for a metric report."""

from functools import lru_cache
from html import escape
import math
from pathlib import Path


@lru_cache(maxsize=1)
def _css():
    return Path(__file__).with_name("style.css").read_text(encoding="utf-8")


def _text(value):
    if value is None or (isinstance(value, float) and not math.isfinite(value)):
        return "—"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, float):
        return format(value, ".5g")
    return escape(str(value), quote=True)


def _recall_figure(metric):
    groups = (metric.get("result") or {}).get("by_tier_role", {})
    rows = []
    for tier in ("control", "rare", "normal", "frequent"):
        pair = [
            groups.get(f"{tier}/{role}", {}).get("top1")
            for role in ("test", "paraphrase")
        ]
        if not all(isinstance(v, (int, float)) and 0 <= v <= 1 for v in pair):
            continue
        marks = "".join(
            f'<i class="mark {role}" style="left:{100*v:.5f}%"></i>'
            for v, role in zip(pair, ("test", "paraphrase"))
        )
        label = f"{tier.capitalize()}, test {pair[0]:.1%}, paraphrase {pair[1]:.1%}"
        rows.append(
            f'<div class="tier">{tier.capitalize()}</div>'
            f'<div class="plot-row" role="img" aria-label="{label}">{marks}</div>'
        )
    if not rows:
        return ""
    ticks = "".join(f'<span style="left:{i}%">{i}</span>' for i in (0, 25, 50, 75, 100))
    return (
        '<figure class="recall"><figcaption><span class="legend filled">Test</span>'
        '<span class="legend open">Paraphrase</span></figcaption><div class="plot">'
        + "".join(rows)
        + f'<div class="ticks">{ticks}</div>'
        '<div class="axis-title">Top-1 recall (%)</div></div></figure>'
    )


def _section(code, metric):
    title = _text(metric["title"])
    columns, rows = metric["columns"], metric["rows"]
    heading = f'<h2><span class="code">{_text(code)}</span>{title}</h2>'
    status = metric.get("status")
    note = f'<p class="note">{_text(status)}</p>' if status and status != "ok" else ""
    if not rows:
        return f'<section>{heading}{note or "<p>No observations.</p>"}</section>'
    numeric = [
        all(r[i] is None or type(r[i]) in (int, float) for r in rows)
        for i in range(len(columns))
    ]

    def cells(row, header=False):
        if len(row) != len(columns):
            raise ValueError(f"{code} has a table row with the wrong column count")
        tag = "th" if header else "td"
        attrs = ' scope="col"' if header else ""
        return (
            "<tr>"
            + "".join(
                f'<{tag}{attrs} class="{"number" if num else "label"}">{_text(value)}</{tag}>'
                for num, value in zip(numeric, row)
            )
            + "</tr>"
        )

    table = (
        f'<div class="table-wrap"><table style="--columns:{len(columns)}" aria-label="{title}">'
        f"<thead>{cells(columns, True)}</thead>"
        f'<tbody>{"".join(cells(row) for row in rows)}</tbody></table></div>'
    )
    figure = _recall_figure(metric) if code == "Q2" else ""
    return f"<section>{heading}{note}{figure}{table}</section>"


def render(report, *, token=None, error=None, path=None):
    """Render offline HTML. A viewer token adds the live checkpoint form."""
    checkpoint = str(report["checkpoint"])
    controls = ""
    if token is not None:
        controls = (
            '<form method="post" action="/run"><label for="checkpoint">Checkpoint path</label>'
            f'<input type="hidden" name="token" value="{_text(token)}">'
            f'<input id="checkpoint" type="text" name="checkpoint" spellcheck="false" required '
            f'value="{_text(checkpoint if path is None else path)}">'
            '<button type="submit">Rerun</button><span id="progress" role="status"></span></form>'
        )
        if error:
            controls += f'<p role="alert" class="error">{_text(error)}</p>'
    metadata = [
        ("Checkpoint", checkpoint),
        ("Step", report.get("step")),
        ("Layer", report.get("layer_index")),
        ("Device", report.get("device")),
    ]
    if "parity" in report:
        metadata.append(
            ("Baseline check", "Passed" if report["parity"]["passed"] else "Failed")
        )
    meta = "".join(
        f"<div><dt>{name}</dt><dd>{_text(val)}</dd></div>"
        for name, val in metadata
        if val is not None
    )
    content = "".join(
        _section(code, metric) for code, metric in report["metrics"].items()
    )
    script = (
        """<script>
document.querySelector('form').addEventListener('submit', function () {
    this.querySelector('button').disabled = true;
    document.getElementById('progress').textContent = 'Running…';
});
window.addEventListener('pageshow', function () {
    document.querySelector('button').disabled = false;
    document.getElementById('progress').textContent = '';
});
</script>"""
        if token is not None
        else ""
    )
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>Memory layer evaluation</title><style>{_css()}</style></head><body>"
        f"<main><header><h1>Memory layer evaluation</h1>{controls}<dl>{meta}</dl></header>"
        f"{content}</main>{script}</body></html>"
    )
