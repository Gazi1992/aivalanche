"""
D3.js Helper Module for Python
Provides a flexible way to create D3 visualizations from Python
"""

import json
from typing import Dict, Any, Optional, Union


def create_d3_viz(d3_code: str, data: Optional[Any] = None,
                  viz_type: str = 'custom', is_animation: bool = False,
                  auto_play: bool = False) -> Dict:
    """
    Create a D3 visualization with maximum flexibility.

    Args:
        d3_code: JavaScript/D3 code as a string that will be executed in the frontend
        data: Any data to pass to the D3 visualization (will be JSON serialized)
        viz_type: Type identifier for the visualization
        is_animation: Whether this visualization contains data that changes over time
        auto_play: If is_animation=True, whether to auto-play on load

    Returns:
        Dictionary containing the D3 configuration

    Note:
        - Width and height are determined by the frontend container dimensions.
        - Set is_animation=True only for visualizations where DATA changes over time,
          not for visual transitions or hover effects.
    """
    config = {
        'type': viz_type,
        'code': d3_code,
        'data': data,
        'isAnimation': is_animation
    }

    if is_animation:
        config['autoPlay'] = auto_play

    return config


def d3_force_graph(nodes: list, links: list, d3_code: Optional[str] = None) -> Dict:
    """
    Create a force-directed graph with custom D3 code.

    Args:
        nodes: List of node objects
        links: List of link objects
        d3_code: Optional custom D3 code to override default behavior

    Returns:
        D3 configuration dictionary
    """
    if d3_code is None:
        # Default force graph code template
        d3_code = """
        // Default force-directed graph
        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.links).id(d => d.id))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2));

        const link = svg.append("g")
            .selectAll("line")
            .data(data.links)
            .enter().append("line")
            .attr("stroke", "#999")
            .attr("stroke-opacity", 0.6);

        const node = svg.append("g")
            .selectAll("circle")
            .data(data.nodes)
            .enter().append("circle")
            .attr("r", d => d.radius || 5)
            .attr("fill", d => d.color || "#69b3a2")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
        });

        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }

        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
        """

    return {
        'type': 'force',
        'code': d3_code,
        'data': {'nodes': nodes, 'links': links}
    }


def d3_hierarchy(hierarchy_data: Dict, layout: str = 'tree', d3_code: Optional[str] = None) -> Dict:
    """
    Create a hierarchical visualization.

    Args:
        hierarchy_data: Hierarchical data structure
        layout: Layout type ('tree', 'cluster', 'treemap', 'pack', 'sunburst')
        d3_code: Optional custom D3 code

    Returns:
        D3 configuration dictionary
    """
    if d3_code is None:
        # Generate default code based on layout
        if layout == 'tree':
            d3_code = """
            const root = d3.hierarchy(data);
            const treeLayout = d3.tree().size([width - 40, height - 40]);
            treeLayout(root);

            const g = svg.append("g").attr("transform", "translate(20,20)");

            // Draw links
            g.selectAll(".link")
                .data(root.links())
                .enter().append("path")
                .attr("class", "link")
                .attr("d", d3.linkVertical()
                    .x(d => d.x)
                    .y(d => d.y))
                .attr("fill", "none")
                .attr("stroke", "#555");

            // Draw nodes
            const node = g.selectAll(".node")
                .data(root.descendants())
                .enter().append("g")
                .attr("class", "node")
                .attr("transform", d => `translate(${d.x},${d.y})`);

            node.append("circle")
                .attr("r", 5)
                .attr("fill", d => d.children ? "#555" : "#999");

            node.append("text")
                .attr("dy", "0.31em")
                .attr("x", d => d.children ? -10 : 10)
                .style("text-anchor", d => d.children ? "end" : "start")
                .text(d => d.data.name);
            """
        else:
            # Default to basic rendering
            d3_code = f"// Custom {layout} layout - implement your D3 code here"

    return {
        'type': 'hierarchy',
        'layout': layout,
        'code': d3_code,
        'data': hierarchy_data
    }


def d3_animation(d3_code: str, data: Any, auto_play: bool = True) -> Dict:
    """
    Create a D3 animation where data changes over time.

    Args:
        d3_code: JavaScript/D3 code that implements animation controls
                 Should return an object with play(), pause(), and stop() methods
        data: Animation data (e.g., time series, snapshots, frames)
        auto_play: Whether to start playing automatically

    Returns:
        D3 configuration dictionary with animation flag set

    Example:
        d3_code = '''
        // Your animation code here
        let currentFrame = 0;

        function updateData() {
            // Update visualization with data[currentFrame]
            currentFrame = (currentFrame + 1) % data.frames.length;
        }

        return {
            play: () => { /* start animation */ },
            pause: () => { /* pause animation */ },
            stop: () => { /* stop and reset */ }
        };
        '''
    """
    return create_d3_viz(d3_code, data, viz_type='animation',
                        is_animation=True, auto_play=auto_play)


def d3_custom(d3_code: str, data: Optional[Any] = None) -> Dict:
    """
    Create a completely custom D3 visualization with full control.

    Args:
        d3_code: Complete D3.js code as a string
        data: Optional data to pass to the visualization

    Returns:
        D3 configuration dictionary

    Example:
        d3_code = '''
        // Your custom D3 code here
        // You have access to: svg, data, width, height

        const circles = svg.selectAll("circle")
            .data(data)
            .enter().append("circle")
            .attr("cx", d => d.x)
            .attr("cy", d => d.y)
            .attr("r", d => d.r)
            .attr("fill", d => d.color);
        '''

        viz = d3_custom(d3_code, data=[
            {"x": 100, "y": 100, "r": 20, "color": "red"},
            {"x": 200, "y": 200, "r": 30, "color": "blue"}
        ])
    """
    return {
        'type': 'custom',
        'code': d3_code,
        'data': data
    }


def register_d3_visualization(d3_config: Dict, viz_id: str, metadata: Optional[Dict] = None):
    """
    Register a D3 visualization with the plot registry.
    This function will be called from the execution environment where register_plot is available.
    """
    # Format as a D3 visualization for the frontend
    d3_figure = {
        'type': 'd3',
        'd3Config': d3_config,
        'metadata': metadata or {}
    }

    # Try to get register_plot from the current frame's locals
    # This is a bit of Python magic to access the caller's namespace
    import inspect
    frame = inspect.currentframe()
    caller_locals = frame.f_back.f_locals

    if 'register_plot' in caller_locals:
        return caller_locals['register_plot'](d3_figure, plot_id=viz_id, metadata=metadata)
    else:
        # Fallback: print message if not in execution environment
        print(f"D3 Visualization '{viz_id}' created (not in execution environment)")
        return viz_id