"""
D3.js Data-Driven Animations Demo
True animations that show data changing over time
"""

import json
import random
import numpy as np

# Demo 1: Time Series Line Chart Animation
# This shows stock price data evolving over time
time_series_data = {
    "timestamps": list(range(100)),
    "series": [
        {
            "name": "Stock A",
            "values": [100 + np.cumsum(np.random.randn(100) * 2).tolist()[i] for i in range(100)]
        },
        {
            "name": "Stock B",
            "values": [100 + np.cumsum(np.random.randn(100) * 2).tolist()[i] for i in range(100)]
        },
        {
            "name": "Stock C",
            "values": [100 + np.cumsum(np.random.randn(100) * 2).tolist()[i] for i in range(100)]
        }
    ]
}

time_series_code = """
// Time series animation showing data progression
const margin = {top: 20, right: 80, bottom: 30, left: 50};
const chartWidth = width - margin.left - margin.right;
const chartHeight = height - margin.top - margin.bottom;

const g = svg.append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

// Scales
const xScale = d3.scaleLinear()
    .domain([0, data.timestamps.length - 1])
    .range([0, chartWidth]);

const yScale = d3.scaleLinear()
    .domain([50, 200])
    .range([chartHeight, 0]);

const colorScale = d3.scaleOrdinal(d3.schemeCategory10);

// Add axes
g.append("g")
    .attr("transform", `translate(0,${chartHeight})`)
    .call(d3.axisBottom(xScale));

g.append("g")
    .call(d3.axisLeft(yScale));

// Line generator
const line = d3.line()
    .x((d, i) => xScale(i))
    .y(d => yScale(d))
    .curve(d3.curveMonotoneX);

// Create paths for each series
const paths = g.selectAll(".series")
    .data(data.series)
    .enter().append("g")
    .attr("class", "series");

const lines = paths.append("path")
    .attr("fill", "none")
    .attr("stroke", (d, i) => colorScale(i))
    .attr("stroke-width", 2);

// Legend
const legend = g.selectAll(".legend")
    .data(data.series)
    .enter().append("g")
    .attr("transform", (d, i) => `translate(${chartWidth + 10}, ${i * 20})`);

legend.append("rect")
    .attr("width", 10)
    .attr("height", 10)
    .attr("fill", (d, i) => colorScale(i));

legend.append("text")
    .attr("x", 15)
    .attr("y", 5)
    .attr("dy", "0.35em")
    .text(d => d.name)
    .style("font-size", "12px");

// Animation state
let currentIndex = 1;
let animationInterval = null;

function updateChart() {
    // Update lines with data up to currentIndex
    lines.attr("d", d => {
        const subset = d.values.slice(0, currentIndex);
        return line(subset);
    });

    currentIndex++;
    if (currentIndex > data.timestamps.length) {
        currentIndex = 1; // Loop back
    }
}

// Return control methods for true data animation
return {
    play: () => {
        if (!animationInterval) {
            animationInterval = d3.interval(updateChart, 50);
        }
    },
    pause: () => {
        if (animationInterval) {
            animationInterval.stop();
            animationInterval = null;
        }
    },
    stop: () => {
        if (animationInterval) {
            animationInterval.stop();
            animationInterval = null;
        }
        currentIndex = 1;
        updateChart();
    },
    // Methods for frame-based export
    getFrameCount: () => data.timestamps.length,
    setFrame: (frameIndex) => {
        currentIndex = Math.min(frameIndex + 1, data.timestamps.length);
        updateChart();
    },
    captureFrames: async (onProgress) => {
        const frames = [];
        const totalFrames = data.timestamps.length;

        for (let i = 0; i < totalFrames; i += 5) { // Sample every 5th frame for smaller GIF
            currentIndex = i + 1;
            updateChart();

            // Wait for render
            await new Promise(resolve => setTimeout(resolve, 10));

            // Capture SVG state
            const svgNode = svg.node();
            const serializer = new XMLSerializer();
            const svgString = serializer.serializeToString(svgNode);
            frames.push(svgString);

            if (onProgress) {
                onProgress((i + 1) / totalFrames);
            }
        }

        currentIndex = 1;
        updateChart();
        return frames;
    }
};
"""

time_series_viz = d3_animation(time_series_code, time_series_data, auto_play=False)
register_d3_visualization(time_series_viz, "time_series_animation",
                         metadata={"title": "Stock Prices Over Time (Data Animation)"})


# Demo 2: Bar Chart Race Animation
# Shows changing rankings over time (like population by country)
bar_race_data = {
    "categories": ["Product A", "Product B", "Product C", "Product D", "Product E"],
    "timepoints": []
}

# Generate data for each timepoint
for t in range(50):
    values = []
    for cat in bar_race_data["categories"]:
        base = random.uniform(50, 100)
        value = base + random.uniform(-20, 20) * (t / 10)
        values.append({"name": cat, "value": max(10, value)})
    bar_race_data["timepoints"].append({
        "time": f"Week {t+1}",
        "values": sorted(values, key=lambda x: x["value"], reverse=True)
    })

bar_race_code = """
// Bar chart race - data changing over time
const margin = {top: 40, right: 30, bottom: 40, left: 100};
const chartWidth = width - margin.left - margin.right;
const chartHeight = height - margin.top - margin.bottom;

const g = svg.append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

// Scales
const xScale = d3.scaleLinear()
    .range([0, chartWidth]);

const yScale = d3.scaleBand()
    .range([0, chartHeight])
    .padding(0.1);

const colorScale = d3.scaleOrdinal(d3.schemeSet2);

// Create axes groups
const xAxis = g.append("g")
    .attr("transform", `translate(0,${chartHeight})`);

const yAxis = g.append("g");

// Title showing current time
const title = svg.append("text")
    .attr("x", width / 2)
    .attr("y", 20)
    .attr("text-anchor", "middle")
    .style("font-size", "18px")
    .style("font-weight", "bold");

// Animation state
let currentTimepoint = 0;
let animationInterval = null;

function updateBars() {
    const currentData = data.timepoints[currentTimepoint];

    // Update title
    title.text(currentData.time);

    // Update scales
    xScale.domain([0, d3.max(currentData.values, d => d.value)]);
    yScale.domain(currentData.values.map(d => d.name));

    // Update axes
    xAxis.transition().duration(300).call(d3.axisBottom(xScale));
    yAxis.transition().duration(300).call(d3.axisLeft(yScale));

    // Bind data to bars
    const bars = g.selectAll(".bar")
        .data(currentData.values, d => d.name);

    // Enter new bars
    bars.enter().append("rect")
        .attr("class", "bar")
        .attr("fill", d => colorScale(d.name))
        .attr("y", d => yScale(d.name))
        .attr("height", yScale.bandwidth())
        .attr("x", 0)
        .attr("width", 0)
      .merge(bars)
        .transition().duration(300)
        .attr("y", d => yScale(d.name))
        .attr("width", d => xScale(d.value));

    // Remove old bars
    bars.exit().remove();

    // Add value labels
    const labels = g.selectAll(".label")
        .data(currentData.values, d => d.name);

    labels.enter().append("text")
        .attr("class", "label")
        .attr("text-anchor", "start")
        .style("font-size", "11px")
      .merge(labels)
        .transition().duration(300)
        .attr("x", d => xScale(d.value) + 5)
        .attr("y", d => yScale(d.name) + yScale.bandwidth() / 2)
        .attr("dy", "0.35em")
        .text(d => d.value.toFixed(1));

    labels.exit().remove();

    // Move to next timepoint
    currentTimepoint = (currentTimepoint + 1) % data.timepoints.length;
}

// Initial render
updateBars();

// Return control methods
return {
    play: () => {
        if (!animationInterval) {
            animationInterval = d3.interval(updateBars, 500);
        }
    },
    pause: () => {
        if (animationInterval) {
            animationInterval.stop();
            animationInterval = null;
        }
    },
    stop: () => {
        if (animationInterval) {
            animationInterval.stop();
            animationInterval = null;
        }
        currentTimepoint = 0;
        updateBars();
    }
};
"""

bar_race_viz = d3_animation(bar_race_code, bar_race_data, auto_play=False)
register_d3_visualization(bar_race_viz, "bar_race_animation",
                         metadata={"title": "Sales Rankings Over Time (Bar Race)"})


# Demo 3: Network Evolution Animation
# Shows a network growing/changing over time
network_evolution_data = {
    "snapshots": []
}

# Generate network snapshots over time
nodes_over_time = []
links_over_time = []

for t in range(30):
    # Start with 3 nodes, add more over time
    num_nodes = min(3 + t, 20)
    nodes = [{"id": i, "group": i % 3, "radius": 5 + random.random() * 10}
             for i in range(num_nodes)]

    # Add links between nodes
    links = []
    for i in range(num_nodes):
        # Each node connects to 1-3 others
        num_connections = min(random.randint(1, 3), num_nodes - 1)
        targets = random.sample([j for j in range(num_nodes) if j != i], num_connections)
        for target in targets:
            if not any(l for l in links if
                      (l["source"] == i and l["target"] == target) or
                      (l["source"] == target and l["target"] == i)):
                links.append({"source": i, "target": target, "weight": random.random()})

    network_evolution_data["snapshots"].append({
        "time": t,
        "nodes": nodes,
        "links": links
    })

network_evolution_code = """
// Network evolution - showing network structure changing over time
const simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(d => d.id).distance(50))
    .force("charge", d3.forceManyBody().strength(-100))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide().radius(d => d.radius + 2));

// Create containers
const linkGroup = svg.append("g").attr("class", "links");
const nodeGroup = svg.append("g").attr("class", "nodes");

// Time display
const timeDisplay = svg.append("text")
    .attr("x", 10)
    .attr("y", 20)
    .style("font-size", "14px")
    .style("font-weight", "bold");

// Color scale
const colorScale = d3.scaleOrdinal(d3.schemeCategory10);

// Animation state
let currentSnapshot = 0;
let animationInterval = null;

function updateNetwork() {
    const snapshot = data.snapshots[currentSnapshot];

    // Update time display
    timeDisplay.text(`Time: ${snapshot.time}`);

    // Update links
    const links = linkGroup.selectAll("line")
        .data(snapshot.links, d => `${d.source}-${d.target}`);

    links.enter().append("line")
        .attr("stroke", "#999")
        .attr("stroke-opacity", 0.6)
        .attr("stroke-width", d => 1 + d.weight * 2)
      .merge(links)
        .attr("stroke-width", d => 1 + d.weight * 2);

    links.exit().remove();

    // Update nodes
    const nodes = nodeGroup.selectAll("circle")
        .data(snapshot.nodes, d => d.id);

    nodes.enter().append("circle")
        .attr("r", d => d.radius)
        .attr("fill", d => colorScale(d.group))
        .attr("stroke", "#fff")
        .attr("stroke-width", 2)
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended))
      .merge(nodes)
        .attr("r", d => d.radius);

    nodes.exit().remove();

    // Update simulation
    simulation.nodes(snapshot.nodes);
    simulation.force("link").links(snapshot.links);
    simulation.alpha(0.3).restart();

    // Update positions on tick
    simulation.on("tick", () => {
        linkGroup.selectAll("line")
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        nodeGroup.selectAll("circle")
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);
    });

    // Move to next snapshot
    currentSnapshot = (currentSnapshot + 1) % data.snapshots.length;
}

// Drag functions
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

// Initial render
updateNetwork();

// Return control methods
return {
    play: () => {
        if (!animationInterval) {
            animationInterval = d3.interval(updateNetwork, 1000);
        }
    },
    pause: () => {
        if (animationInterval) {
            animationInterval.stop();
            animationInterval = null;
        }
    },
    stop: () => {
        if (animationInterval) {
            animationInterval.stop();
            animationInterval = null;
        }
        currentSnapshot = 0;
        updateNetwork();
    }
};
"""

network_viz = d3_animation(network_evolution_code, network_evolution_data, auto_play=False)
register_d3_visualization(network_viz, "network_evolution",
                         metadata={"title": "Network Evolution Over Time"})


# Demo 4: Scatter Plot Animation - Population vs GDP over years
scatter_animation_data = {
    "years": list(range(2000, 2025)),
    "countries": ["USA", "China", "India", "Germany", "Japan", "Brazil"],
    "data": []
}

# Generate data for each year
for year in scatter_animation_data["years"]:
    year_data = []
    for i, country in enumerate(scatter_animation_data["countries"]):
        # Simulate changing GDP and population
        base_gdp = [20000, 15000, 8000, 18000, 17000, 10000][i]
        base_pop = [300, 1400, 1350, 80, 125, 210][i]

        gdp = base_gdp + (year - 2000) * random.uniform(500, 1500)
        population = base_pop + (year - 2000) * random.uniform(-2, 5)

        year_data.append({
            "country": country,
            "gdp": gdp,
            "population": population,
            "year": year
        })
    scatter_animation_data["data"].append(year_data)

scatter_code = """
// Animated scatter plot showing data evolution
const margin = {top: 40, right: 100, bottom: 50, left: 60};
const chartWidth = width - margin.left - margin.right;
const chartHeight = height - margin.top - margin.bottom;

const g = svg.append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

// Scales
const xScale = d3.scaleLinear()
    .domain([0, 1500])
    .range([0, chartWidth]);

const yScale = d3.scaleLinear()
    .domain([5000, 40000])
    .range([chartHeight, 0]);

const sizeScale = d3.scaleSqrt()
    .domain([0, 40000])
    .range([5, 30]);

const colorScale = d3.scaleOrdinal(d3.schemeSet1);

// Add axes
g.append("g")
    .attr("transform", `translate(0,${chartHeight})`)
    .call(d3.axisBottom(xScale))
  .append("text")
    .attr("x", chartWidth / 2)
    .attr("y", 40)
    .style("text-anchor", "middle")
    .style("fill", "#000")
    .text("Population (millions)");

g.append("g")
    .call(d3.axisLeft(yScale))
  .append("text")
    .attr("transform", "rotate(-90)")
    .attr("y", -40)
    .attr("x", -chartHeight / 2)
    .style("text-anchor", "middle")
    .style("fill", "#000")
    .text("GDP per Capita ($)");

// Year display
const yearDisplay = svg.append("text")
    .attr("x", width / 2)
    .attr("y", 25)
    .attr("text-anchor", "middle")
    .style("font-size", "24px")
    .style("font-weight", "bold")
    .style("opacity", 0.7);

// Legend
const legend = g.selectAll(".legend")
    .data(data.countries)
    .enter().append("g")
    .attr("transform", (d, i) => `translate(${chartWidth + 10}, ${i * 20})`);

legend.append("circle")
    .attr("r", 5)
    .attr("fill", (d, i) => colorScale(i));

legend.append("text")
    .attr("x", 10)
    .attr("y", 0)
    .attr("dy", "0.35em")
    .text(d => d)
    .style("font-size", "12px");

// Animation state
let currentYear = 0;
let animationInterval = null;

function updateScatter() {
    const yearData = data.data[currentYear];
    const year = data.years[currentYear];

    // Update year display
    yearDisplay.text(year);

    // Bind data
    const circles = g.selectAll(".bubble")
        .data(yearData, d => d.country);

    // Enter + Update
    circles.enter().append("circle")
        .attr("class", "bubble")
        .attr("fill", (d, i) => colorScale(i))
        .attr("stroke", "#fff")
        .attr("stroke-width", 2)
        .attr("opacity", 0.7)
      .merge(circles)
        .transition().duration(500)
        .attr("cx", d => xScale(d.population))
        .attr("cy", d => yScale(d.gdp))
        .attr("r", d => sizeScale(d.gdp));

    // Move to next year
    currentYear = (currentYear + 1) % data.years.length;
}

// Initial render
updateScatter();

// Return control methods
return {
    play: () => {
        if (!animationInterval) {
            animationInterval = d3.interval(updateScatter, 800);
        }
    },
    pause: () => {
        if (animationInterval) {
            animationInterval.stop();
            animationInterval = null;
        }
    },
    stop: () => {
        if (animationInterval) {
            animationInterval.stop();
            animationInterval = null;
        }
        currentYear = 0;
        updateScatter();
    }
};
"""

scatter_viz = d3_animation(scatter_code, scatter_animation_data, auto_play=False)
register_d3_visualization(scatter_viz, "scatter_animation",
                         metadata={"title": "GDP vs Population Over Time"})

print("D3 data-driven animations demo created with 4 true data animations")