"""Small, accessible metric panels and factual citation sparklines."""
from html import escape
from open_metrics import nonnegative, METRIC, H_INDEX


def sparkline_svg(history, start=2021, end=2025):
    points = {int(item['year']): nonnegative(item.get('citations')) for item in history
              if isinstance(item.get('year'), int) and start <= item['year'] <= end}
    values = [points.get(year) for year in range(start, end + 1)]
    available = [value for value in values if value is not None]
    if not available:
        return '<span style="color:#64748b;font-size:12px">Histórico anual indisponível</span>'
    high = max(available) or 1
    descriptions = [f'{year}: {value:g} citações' if value is not None else f'{year}: sem registro'
                    for year, value in zip(range(start, end + 1), values)]
    segments, current, circles = [], [], []
    for position, (year, value) in enumerate(zip(range(start, end + 1), values)):
        x = 12 + position * 56
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
    labels = ''.join(f'<text x="{12 + position * 56}" y="73" font-size="10" text-anchor="middle" fill="#64748b">{year}</text>' for position, year in enumerate(range(start, end + 1)))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 250 80" role="img" aria-label="' + escape('; '.join(descriptions), quote=True) + '" style="width:250px;max-width:100%;height:80px;display:block">'
            '<path d="M12,57 L236,57" stroke="#dbe8e5" fill="none"/>' + paths + ''.join(circles) + labels + '</svg>')


def metric_panel(row):
    blocks = []
    for field, label, icon, foreground, background in [
        (METRIC, 'Média de citações · 2 anos', '↗', '#1d4ed8', '#eff6ff'),
        (H_INDEX, 'Índice h', '◆', '#0f766e', '#ecfdf5'),
    ]:
        value = nonnegative(row.get(field))
        if value is None:
            continue
        formatted = f'{value:.2f}'.replace('.', ',') if field == METRIC else f'{int(value):,}'.replace(',', '.')
        blocks.append(f'<div style="background:{background};border:1px solid {foreground}22;border-radius:12px;padding:12px 16px;min-width:145px;flex:1">'
                      f'<div style="font-size:12px;color:{foreground};white-space:normal">{icon} {label}</div>'
                      f'<div style="font-size:27px;font-weight:750;color:{foreground};line-height:1.3;font-variant-numeric:tabular-nums">{formatted}</div>'
                      '<div style="font-size:10px;color:#64748b">OpenAlex</div></div>')
    history = row.get('_citation_history') or []
    if history:
        blocks.append('<div style="border:1px solid #dbe8e5;background:#fbfefd;border-radius:12px;padding:10px 14px;flex:1;min-width:230px">'
                      '<div style="font-size:12px;font-weight:650;color:#0f766e">Citações por ano · OpenAlex</div>'
                      + sparkline_svg(history) + '</div>')
    return '<div style="display:flex;gap:10px;flex-wrap:wrap;margin:10px 0">' + ''.join(blocks) + '</div>'


def journal_chips(area, publisher, full):
    label = 'Cobertura integral indicada' if full else 'Conferir cobertura'
    color, background = ('#166534', '#dcfce7') if full else ('#92400e', '#fef3c7')
    return ('<div style="display:flex;gap:7px;flex-wrap:wrap;margin:6px 0">'
            '<span style="border-radius:99px;background:#eff6ff;color:#1e40af;padding:4px 10px;font-size:12px">● ' + escape(str(area)) + '</span>'
            '<span style="border-radius:99px;background:#f1f5f9;color:#475569;padding:4px 10px;font-size:12px">' + escape(str(publisher)) + '</span>'
            f'<span style="border-radius:99px;background:{background};color:{color};padding:4px 10px;font-size:12px">{label}</span></div>')
