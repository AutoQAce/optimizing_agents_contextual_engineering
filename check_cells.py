import json

nb = json.load(open('optimizing_agents_contextual_engineering.ipynb', 'r', encoding='utf-8'))
for i, c in enumerate(nb['cells']):
    src = c.get('source', [])
    preview = src[0][:100].strip() if src else '(empty)'
    print(f"Cell {i}: {c['cell_type']}, {len(src)} lines | {preview}")