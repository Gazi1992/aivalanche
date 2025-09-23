"""
Analyze all demo scripts to identify unique plot types
"""

import os
import re
from collections import defaultdict

demo_dir = "backend/demo_scripts"
plot_types = defaultdict(list)

# Patterns to identify plot types
patterns = {
    'scatter': r'go\.Scatter\(',
    'scatter3d': r'go\.Scatter3d\(',
    'scattergl': r'go\.Scattergl\(',
    'scatterpolar': r'go\.Scatterpolar\(',
    'scatterternary': r'go\.Scatterternary\(',
    'scattergeo': r'go\.Scattergeo\(',
    'scattermapbox': r'go\.Scattermapbox\(',
    'bar': r'go\.Bar\(',
    'line': r'go\.Scatter\(.*mode=[\'"]lines',
    'area': r'go\.Scatter\(.*fill=',
    'pie': r'go\.Pie\(',
    'donut': r'go\.Pie\(.*hole=',
    'sunburst': r'go\.Sunburst\(',
    'treemap': r'go\.Treemap\(',
    'funnel': r'go\.Funnel\(',
    'funnelarea': r'go\.Funnelarea\(',
    'indicator': r'go\.Indicator\(',
    'box': r'go\.Box\(',
    'violin': r'go\.Violin\(',
    'histogram': r'go\.Histogram\(',
    'histogram2d': r'go\.Histogram2d\(',
    'heatmap': r'go\.Heatmap\(',
    'contour': r'go\.Contour\(',
    'surface': r'go\.Surface\(',
    'mesh3d': r'go\.Mesh3d\(',
    'isosurface': r'go\.Isosurface\(',
    'volume': r'go\.Volume\(',
    'cone': r'go\.Cone\(',
    'streamtube': r'go\.Streamtube\(',
    'candlestick': r'go\.Candlestick\(',
    'ohlc': r'go\.Ohlc\(',
    'waterfall': r'go\.Waterfall\(',
    'sankey': r'go\.Sankey\(',
    'parcats': r'go\.Parcats\(',
    'parcoords': r'go\.Parcoords\(',
    'carpet': r'go\.Carpet\(',
    'table': r'go\.Table\(',
    'densitymapbox': r'go\.Densitymapbox\(',
    'choroplethmapbox': r'go\.Choroplethmapbox\(',
    'choropleth': r'go\.Choropleth\(',
    'splom': r'go\.Splom\(',
}

# Also check for plotly express patterns
px_patterns = {
    'scatter_matrix': r'px\.scatter_matrix\(',
    'parallel_coordinates': r'px\.parallel_coordinates\(',
    'parallel_categories': r'px\.parallel_categories\(',
    'density_heatmap': r'px\.density_heatmap\(',
    'density_contour': r'px\.density_contour\(',
    'imshow': r'px\.imshow\(',
    'line_3d': r'px\.line_3d\(',
    'scatter_3d': r'px\.scatter_3d\(',
    'strip': r'px\.strip\(',
    'ecdf': r'px\.ecdf\(',
    'timeline': r'px\.timeline\(',
    'treemap': r'px\.treemap\(',
    'sunburst': r'px\.sunburst\(',
    'icicle': r'px\.icicle\(',
}

# Analyze each demo file
for filename in os.listdir(demo_dir):
    if filename.endswith('.py'):
        filepath = os.path.join(demo_dir, filename)
        with open(filepath, 'r') as f:
            content = f.read()

        print(f"\n=== {filename} ===")
        found_types = set()

        # Check go. patterns
        for plot_type, pattern in patterns.items():
            if re.search(pattern, content):
                plot_types[plot_type].append(filename)
                found_types.add(plot_type)

        # Check px. patterns
        for plot_type, pattern in px_patterns.items():
            if re.search(pattern, content):
                plot_types[f"px_{plot_type}"].append(filename)
                found_types.add(f"px_{plot_type}")

        # Also check for figure_factory
        if 'ff.' in content:
            if 'create_distplot' in content:
                found_types.add('ff_distplot')
            if 'create_dendrogram' in content:
                found_types.add('ff_dendrogram')
            if 'create_annotated_heatmap' in content:
                found_types.add('ff_annotated_heatmap')

        print(f"Found plot types: {', '.join(sorted(found_types))}")

print("\n\n=== SUMMARY OF UNIQUE PLOT TYPES ===")
print(f"Total unique plot types found: {len(plot_types)}")
print("\nBy frequency:")
sorted_types = sorted(plot_types.items(), key=lambda x: len(x[1]), reverse=True)
for plot_type, files in sorted_types:
    print(f"  {plot_type}: {len(files)} files - {', '.join(files)}")

print("\n\n=== CATEGORIZATION ===")
categories = {
    "Basic 2D Plots": ['scatter', 'line', 'bar', 'area'],
    "Statistical Plots": ['box', 'violin', 'histogram', 'histogram2d', 'strip', 'ecdf', 'ff_distplot'],
    "Part-to-Whole": ['pie', 'donut', 'sunburst', 'treemap', 'icicle', 'funnel', 'funnelarea'],
    "Heatmaps & Density": ['heatmap', 'contour', 'density_heatmap', 'density_contour', 'ff_annotated_heatmap'],
    "3D Plots": ['scatter3d', 'surface', 'mesh3d', 'isosurface', 'volume', 'cone', 'streamtube', 'line_3d', 'px_scatter_3d'],
    "Financial/Time Series": ['candlestick', 'ohlc', 'waterfall', 'timeline'],
    "Multi-dimensional": ['parcoords', 'parcats', 'scatter_matrix', 'splom', 'parallel_coordinates', 'parallel_categories'],
    "Flow & Network": ['sankey'],
    "Specialized": ['indicator', 'table', 'scatterpolar', 'scatterternary', 'carpet'],
    "Geographic": ['scattergeo', 'scattermapbox', 'choropleth', 'choroplethmapbox', 'densitymapbox'],
}

print("\nCategorized plot types:")
for category, types in categories.items():
    existing = [t for t in types if t in plot_types or f"px_{t}" in plot_types]
    print(f"\n{category}:")
    print(f"  {', '.join(existing)}")