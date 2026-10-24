"""Small, accessible metric panels and factual citation sparklines."""
from html import escape
from scholar_metrics import scholar_panel
from open_metrics import nonnegative, METRIC, H_INDEX


def sparkline_svg(history, start=2021, end=2025):
    points = {int(item['year']): nonnegative(item.get('citations')) for item in history
              if isinstance(item.get('year'), int) and start <= item['year'] <= end}
    values = [points.get(year) for year in range(start, end + 1)]
    available = [value for value in values if value is not None]
    if not available:
        return '<span style="color:#475569;font-size:.875rem">Histórico anual indisponível</span>'
    high = max(available) or 1
    descriptions = [f'{year}: {value:g} citações' if value is not None else f'{year}: sem registro'
                    for year, value in zip(range(start, end + 1), values)]
    segments, current, circles = [], [], []
    for position, (year, value) in enumerate(zip(range(start, end + 1), values)):
        x = 18 + position * 53
        if value is None:
            if current:
                segments.append(current)
                current = []
            continue
        y = 53 - (value / high) * 42
        current.append((x, y))
        circles.append(f'<circle cx="{x}" cy="{y:.2f}" r="3.8" fill="#0f766e"><title>{year}: {value:g} citações</title></circle>')
    if current:
        segments.append(current)
    paths = ''.join('<path d="' + ' '.join(('M' if index == 0 else 'L') + f'{x},{y:.2f}' for index, (x, y) in enumerate(segment)) + '" fill="none" stroke="#0f766e" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>' for segment in segments)
    labels = ''.join(f'<text x="{18 + position * 53}" y="76" font-size="14" font-family="Arial, Helvetica, sans-serif" text-anchor="middle" fill="#475569">{year}</text>' for position, year in enumerate(range(start, end + 1)))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 250 80" role="img" aria-label="' + escape('; '.join(descriptions), quote=True) + '" style="width:15.625rem;max-width:100%;height:5rem;display:block">'
            '<path d="M18,57 L230,57" stroke="#dbe8e5" fill="none"/>' + paths + ''.join(circles) + labels + '</svg>')


def metric_panel(row):
    blocks = []
    for field, label, icon, foreground, background in [
        (METRIC, 'Média de citações · 2 anos', '↗', '#1d4ed8', '#eff6ff'),
        (H_INDEX, 'Índice h · OpenAlex', '◆', '#0f766e', '#ecfdf5'),
    ]:
        value = nonnegative(row.get(field))
        if value is None:
            continue
        formatted = f'{value:.2f}'.replace('.', ',') if field == METRIC else f'{int(value):,}'.replace(',', '.')
        blocks.append(f'<div style="background:{background};border:1px solid {foreground}22;border-radius:12px;padding:12px 16px;min-width:0;flex:1 1 10rem">'
                      f'<div style="font-size:.875rem;color:{foreground};white-space:normal">{icon} {label}</div>'
                      f'<div style="font-size:1.875rem;font-weight:750;color:{foreground};line-height:1.3;font-variant-numeric:tabular-nums">{formatted}</div>'
                      '<div style="font-size:.875rem;color:#475569">OpenAlex</div></div>')
    history = row.get('_citation_history') or []
    if history:
        blocks.append('<div style="border:1px solid #dbe8e5;background:#fbfefd;border-radius:12px;padding:10px 14px;flex:1 1 16rem;min-width:0">'
                      '<div style="font-size:.875rem;font-weight:650;color:#0f766e">Citações por ano · OpenAlex</div>'
                      + sparkline_svg(history) + '</div>')
    heading = '<div style="font-weight:700;color:#0f766e;margin-top:14px">Métricas OpenAlex</div>' if blocks else ''
    return heading + '<div style="display:flex;gap:10px;flex-wrap:wrap;margin:10px 0">' + ''.join(blocks) + '</div>' + scholar_panel(row.get('Título da Revista', ''), row.get('ISSN'))


def journal_chips(area, publisher, full):
    label = 'Cobertura integral indicada' if full else 'Conferir cobertura'
    color, background = ('#166534', '#dcfce7') if full else ('#92400e', '#fef3c7')
    return ('<div style="display:flex;gap:7px;flex-wrap:wrap;margin:6px 0">'
            '<span style="border-radius:99px;background:#eff6ff;color:#1e40af;padding:4px 10px;font-size:.875rem">● ' + escape(str(area)) + '</span>'
            '<span style="border-radius:99px;background:#f1f5f9;color:#475569;padding:4px 10px;font-size:.875rem">' + escape(str(publisher)) + '</span>'
            f'<span style="border-radius:99px;background:{background};color:{color};padding:4px 10px;font-size:.875rem">{label}</span></div>')
