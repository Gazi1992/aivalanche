"""
Demo Index - Central registry of all demo scripts
"""

DEMO_CATEGORIES = {
    'climate': {
        'name': '🌍 Climate & Environment',
        'description': 'Climate change and environmental data visualizations',
        'icon': '🌍',
        'color': '#2E7D32',
        'demos': {
            'temperature_anomaly': {
                'file': 'climate/temperature_anomaly.py',
                'name': 'Global Temperature Anomaly',
                'description': 'Temperature changes from 1880-2024 with contour plots'
            },
            'climate_variables': {
                'file': 'climate/climate_variables.py',
                'name': 'Climate Variables Analysis',
                'description': 'CO2, sea level, ice coverage & temperature correlations'
            }
        }
    },
    'space': {
        'name': '🚀 Space & Astronomy',
        'description': 'Astronomical data and space exploration',
        'icon': '🚀',
        'color': '#1565C0',
        'demos': {
            'solar_system': {
                'file': 'space/solar_system.py',
                'name': 'Solar System Simulation',
                'description': 'Interactive D3 orbital mechanics visualization'
            }
        }
    },
    'finance': {
        'name': '💹 Financial Markets',
        'description': 'Market analysis and portfolio risk assessment',
        'icon': '💹',
        'color': '#6A1B9A',
        'demos': {
            'portfolio_risk': {
                'file': 'finance/portfolio_risk.py',
                'name': 'Portfolio Risk Analysis',
                'description': 'Violin and box plots for return distributions'
            }
        }
    },
    'healthcare': {
        'name': '🧬 Healthcare & Medicine',
        'description': 'Medical data and health analytics',
        'icon': '🧬',
        'color': '#C62828',
        'demos': {}
    },
    'urban': {
        'name': '🏙️ Urban & Transportation',
        'description': 'City infrastructure and transport systems',
        'icon': '🏙️',
        'color': '#FF6F00',
        'demos': {}
    },
    'energy': {
        'name': '⚡ Energy & Resources',
        'description': 'Energy production and resource management',
        'icon': '⚡',
        'color': '#F57C00',
        'demos': {}
    },
    'sports': {
        'name': '🎮 Sports & Entertainment',
        'description': 'Performance analytics and entertainment metrics',
        'icon': '🎮',
        'color': '#D32F2F',
        'demos': {}
    },
    'science': {
        'name': '🔬 Scientific Research',
        'description': 'Scientific data and research visualizations',
        'icon': '🔬',
        'color': '#7B1FA2',
        'demos': {}
    },
    'social': {
        'name': '📊 Social & Demographics',
        'description': 'Population and social network analysis',
        'icon': '📊',
        'color': '#0288D1',
        'demos': {}
    },
    'history': {
        'name': '🏛️ Historical Insights',
        'description': 'Historical data and temporal analysis',
        'icon': '🏛️',
        'color': '#5D4037',
        'demos': {}
    },
    'statistical': {
        'name': '🧪 Statistical Showcase',
        'description': 'Advanced statistical visualization techniques',
        'icon': '🧪',
        'color': '#00695C',
        'demos': {
            'multivariate': {
                'file': 'statistical/multivariate.py',
                'name': 'Multivariate Analysis',
                'description': 'SPLOM and Parallel Coordinates for high-dimensional data'
            }
        }
    },
    'geospatial': {
        'name': '🗺️ Geospatial Analysis',
        'description': 'Geographic and spatial data visualization',
        'icon': '🗺️',
        'color': '#4527A0',
        'demos': {}
    }
}

def get_demo_script(category, demo_name):
    """Get the path to a specific demo script"""
    if category in DEMO_CATEGORIES:
        if demo_name in DEMO_CATEGORIES[category]['demos']:
            return DEMO_CATEGORIES[category]['demos'][demo_name]['file']
    return None

def get_all_demos():
    """Get all available demos organized by category"""
    result = []
    for cat_id, category in DEMO_CATEGORIES.items():
        if category['demos']:  # Only include categories with demos
            result.append({
                'id': cat_id,
                'name': category['name'],
                'description': category['description'],
                'icon': category['icon'],
                'color': category['color'],
                'demos': list(category['demos'].keys())
            })
    return result