"""
D3.js Visualizations Demo
Demonstrates various D3 visualizations with maximum flexibility
"""

import random
import json

# Demo 1: Force-directed graph with custom D3 code
nodes = [
    {"id": i, "label": f"Node {i}", "radius": random.uniform(8, 15), "group": i % 3}
    for i in range(20)
]

links = []
for i in range(20):
    for j in range(i + 1, min(i + 3, 20)):
        links.append({
            "source": i,
            "target": j,
            "value": random.uniform(1, 5)
        })

# Use the helper function for a force graph
force_viz = d3_force_graph(nodes, links)
register_d3_visualization(force_viz, "force_graph_demo",
                         metadata={"title": "Interactive Force-Directed Network"})


# Demo 2: Custom animated bubbles with D3
bubble_data = [
    {
        "x": random.uniform(100, 700),
        "y": random.uniform(100, 500),
        "r": random.uniform(10, 50),
        "color": f"hsl({random.randint(0, 360)}, 70%, 50%)",
        "value": random.uniform(1, 100)
    }
    for _ in range(30)
]

bubble_code = """
// Animated bubble chart
const bubbles = svg.selectAll("circle")
    .data(data)
    .enter().append("circle")
    .attr("cx", d => d.x)
    .attr("cy", d => d.y)
    .attr("r", 0)
    .attr("fill", d => d.color)
    .attr("fill-opacity", 0.6)
    .attr("stroke", "#fff")
    .attr("stroke-width", 2);

// Animate bubbles appearing
bubbles.transition()
    .duration(1000)
    .delay((d, i) => i * 50)
    .attr("r", d => d.r);

// Add hover interactions
bubbles.on("mouseover", function(event, d) {
    d3.select(this)
        .transition()
        .duration(200)
        .attr("r", d.r * 1.2)
        .attr("fill-opacity", 0.8);
})
.on("mouseout", function(event, d) {
    d3.select(this)
        .transition()
        .duration(200)
        .attr("r", d.r)
        .attr("fill-opacity", 0.6);
});

// Add tooltips
const tooltip = d3.select("body").append("div")
    .attr("class", "d3-tooltip")
    .style("opacity", 0)
    .style("position", "absolute")
    .style("background", "rgba(0, 0, 0, 0.8)")
    .style("color", "white")
    .style("padding", "5px")
    .style("border-radius", "3px");

bubbles.on("mousemove", function(event, d) {
    tooltip.transition()
        .duration(200)
        .style("opacity", .9);
    tooltip.html(`Value: ${d.value.toFixed(2)}`)
        .style("left", (event.pageX + 10) + "px")
        .style("top", (event.pageY - 28) + "px");
})
.on("mouseleave", function(d) {
    tooltip.transition()
        .duration(500)
        .style("opacity", 0);
});
"""

bubble_viz = create_d3_viz(bubble_code, bubble_data)
register_d3_visualization(bubble_viz, "animated_bubbles",
                         metadata={"title": "Interactive Bubble Chart"})


# Demo 3: Hierarchical tree visualization
org_data = {
    "name": "CEO",
    "value": 100,
    "children": [
        {
            "name": "CTO",
            "value": 80,
            "children": [
                {"name": "Dev Lead", "value": 60, "children": [
                    {"name": "Senior Dev", "value": 40},
                    {"name": "Junior Dev", "value": 30}
                ]},
                {"name": "QA Lead", "value": 50, "children": [
                    {"name": "QA Engineer", "value": 35}
                ]}
            ]
        },
        {
            "name": "CFO",
            "value": 75,
            "children": [
                {"name": "Controller", "value": 55},
                {"name": "Treasurer", "value": 45}
            ]
        },
        {
            "name": "CMO",
            "value": 70,
            "children": [
                {"name": "Marketing Lead", "value": 50},
                {"name": "Sales Lead", "value": 55}
            ]
        }
    ]
}

tree_viz = d3_hierarchy(org_data, layout='tree')
register_d3_visualization(tree_viz, "org_tree",
                         metadata={"title": "Organization Hierarchy"})


# Demo 4: Custom real-time line chart animation
line_code = """
// Real-time updating line chart
const margin = {top: 20, right: 20, bottom: 30, left: 50};
const chartWidth = width - margin.left - margin.right;
const chartHeight = height - margin.top - margin.bottom;

const g = svg.append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

// Generate initial data
let data = d3.range(50).map(i => ({
    x: i,
    y: Math.sin(i / 5) * 50 + Math.random() * 20 + chartHeight / 2
}));

// Set up scales
const x = d3.scaleLinear()
    .domain([0, 49])
    .range([0, chartWidth]);

const y = d3.scaleLinear()
    .domain([0, chartHeight])
    .range([chartHeight, 0]);

// Create line generator
const line = d3.line()
    .x(d => x(d.x))
    .y(d => y(d.y))
    .curve(d3.curveBasis);

// Add axes
g.append("g")
    .attr("transform", `translate(0,${chartHeight})`)
    .call(d3.axisBottom(x));

g.append("g")
    .call(d3.axisLeft(y));

// Add the line
const path = g.append("path")
    .datum(data)
    .attr("fill", "none")
    .attr("stroke", "#00ff00")
    .attr("stroke-width", 2)
    .attr("d", line);

// Animate the line
function tick() {
    // Push new data point
    data.push({
        x: data.length,
        y: Math.sin(data.length / 5) * 50 + Math.random() * 20 + chartHeight / 2
    });

    // Remove old data point
    data.shift();

    // Update x domain
    x.domain([data[0].x, data[data.length - 1].x]);

    // Redraw line
    path.datum(data)
        .attr("d", line)
        .attr("transform", null)
        .transition()
        .duration(500)
        .ease(d3.easeLinear)
        .attr("transform", `translate(${x(-1)},0)`)
        .on("end", tick);
}

// Start animation after a delay
setTimeout(tick, 1000);
"""

realtime_viz = create_d3_viz(line_code, None)
register_d3_visualization(realtime_viz, "realtime_line",
                         metadata={"title": "Real-time Data Stream"})


# Demo 5: Interactive radial chart
radial_code = """
// Radial/sunburst chart
const radius = Math.min(width, height) / 2;

const g = svg.append("g")
    .attr("transform", `translate(${width/2},${height/2})`);

// Create sample data
const data = {
    name: "root",
    children: [
        {
            name: "Analytics",
            children: [
                { name: "Cluster", value: 3938 },
                { name: "Graph", value: 3812 },
                { name: "Optimization", value: 6714 }
            ]
        },
        {
            name: "Visualization",
            children: [
                { name: "Display", value: 3534 },
                { name: "Geometry", value: 7700 },
                { name: "Physics", value: 5731 }
            ]
        },
        {
            name: "Methods",
            children: [
                { name: "Iteration", value: 3534 },
                { name: "Recursion", value: 5731 },
                { name: "Functional", value: 7840 }
            ]
        }
    ]
};

// Create hierarchy
const root = d3.hierarchy(data)
    .sum(d => d.value)
    .sort((a, b) => b.value - a.value);

// Create partition layout
const partition = d3.partition()
    .size([2 * Math.PI, radius]);

partition(root);

// Color scale
const color = d3.scaleOrdinal(d3.schemeSet3);

// Create arc generator
const arc = d3.arc()
    .startAngle(d => d.x0)
    .endAngle(d => d.x1)
    .innerRadius(d => d.y0)
    .outerRadius(d => d.y1);

// Draw arcs
const arcs = g.selectAll("path")
    .data(root.descendants())
    .enter().append("path")
    .attr("d", arc)
    .style("fill", d => color(d.data.name))
    .style("stroke", "#fff")
    .style("stroke-width", 2)
    .style("cursor", "pointer");

// Add interactivity
arcs.on("mouseover", function(event, d) {
    d3.select(this)
        .transition()
        .duration(200)
        .style("opacity", 0.8);
})
.on("mouseout", function(event, d) {
    d3.select(this)
        .transition()
        .duration(200)
        .style("opacity", 1);
})
.on("click", function(event, d) {
    // Zoom to clicked arc
    const transition = g.transition().duration(750);

    arcs.transition(transition)
        .attrTween("d", function(node) {
            const i = d3.interpolate({x0: node.x0, x1: node.x1, y0: node.y0, y1: node.y1},
                                    {x0: node.x0, x1: node.x1, y0: 0, y1: radius});
            return function(t) {
                const b = i(t);
                return arc(b);
            };
        });
});

// Add labels
const labels = g.selectAll("text")
    .data(root.descendants().filter(d => d.depth))
    .enter().append("text")
    .attr("transform", d => {
        const angle = (d.x0 + d.x1) / 2 * 180 / Math.PI - 90;
        const radius = (d.y0 + d.y1) / 2;
        return `rotate(${angle}) translate(${radius},0) rotate(${angle > 90 ? 180 : 0})`;
    })
    .attr("text-anchor", "middle")
    .attr("dy", "0.35em")
    .text(d => d.data.name)
    .style("font-size", "12px")
    .style("fill", "white");
"""

radial_viz = create_d3_viz(radial_code, None)
register_d3_visualization(radial_viz, "radial_chart",
                         metadata={"title": "Interactive Radial Chart"})


# Demo 6: Particle system
particle_code = """
// Particle system simulation
const particles = d3.range(200).map(i => ({
    x: Math.random() * width,
    y: Math.random() * height,
    vx: (Math.random() - 0.5) * 2,
    vy: (Math.random() - 0.5) * 2,
    r: Math.random() * 3 + 1,
    color: d3.interpolateRainbow(i / 200)
}));

const circles = svg.selectAll("circle")
    .data(particles)
    .enter().append("circle")
    .attr("r", d => d.r)
    .attr("fill", d => d.color)
    .attr("fill-opacity", 0.8);

function updateParticles() {
    particles.forEach(p => {
        p.x += p.vx;
        p.y += p.vy;

        // Bounce off walls
        if (p.x <= 0 || p.x >= width) p.vx *= -1;
        if (p.y <= 0 || p.y >= height) p.vy *= -1;

        // Keep in bounds
        p.x = Math.max(p.r, Math.min(width - p.r, p.x));
        p.y = Math.max(p.r, Math.min(height - p.r, p.y));
    });

    circles
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);
}

// Animation loop
d3.timer(updateParticles);

// Add mouse interaction
svg.on("mousemove", function(event) {
    const [mx, my] = d3.pointer(event);

    particles.forEach(p => {
        const dx = mx - p.x;
        const dy = my - p.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 100) {
            const force = (100 - dist) / 100;
            p.vx += (dx / dist) * force * 0.5;
            p.vy += (dy / dist) * force * 0.5;
        }
    });
});
"""

particle_viz = create_d3_viz(particle_code, None)
register_d3_visualization(particle_viz, "particle_system",
                         metadata={"title": "Interactive Particle System"})

print("D3 visualizations demo completed! 6 interactive visualizations created.")