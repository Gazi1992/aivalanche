"""
🚀 Solar System Orbital Simulation
Interactive D3 visualization with realistic orbital mechanics
"""

import json

# Planetary data with realistic orbital parameters
planets = [
    {"name": "Mercury", "radius": 4, "distance": 40, "period": 0.24, "color": "#8C7853"},
    {"name": "Venus", "radius": 7, "distance": 70, "period": 0.62, "color": "#FFC649"},
    {"name": "Earth", "radius": 7, "distance": 100, "period": 1.0, "color": "#4A90E2"},
    {"name": "Mars", "radius": 5, "distance": 140, "period": 1.88, "color": "#CD5C5C"},
    {"name": "Jupiter", "radius": 15, "distance": 220, "period": 11.86, "color": "#DAA520"},
    {"name": "Saturn", "radius": 12, "distance": 300, "period": 29.46, "color": "#F4E4C1"},
]

# D3 code for solar system animation
solar_system_code = """
// Solar System Animation with Realistic Orbits
const centerX = width / 2;
const centerY = height / 2;
const scale = Math.min(width, height) / 700;

// Create gradient for sun
const sunGradient = svg.append("defs")
    .append("radialGradient")
    .attr("id", "sun-gradient");

sunGradient.append("stop")
    .attr("offset", "0%")
    .attr("stop-color", "#FFF5B4");

sunGradient.append("stop")
    .attr("offset", "50%")
    .attr("stop-color", "#FFEE00");

sunGradient.append("stop")
    .attr("offset", "100%")
    .attr("stop-color", "#FF9900");

// Add glow effect for sun
const filter = svg.append("defs")
    .append("filter")
    .attr("id", "glow");

filter.append("feGaussianBlur")
    .attr("stdDeviation", "4")
    .attr("result", "coloredBlur");

const feMerge = filter.append("feMerge");
feMerge.append("feMergeNode").attr("in", "coloredBlur");
feMerge.append("feMergeNode").attr("in", "SourceGraphic");

// Draw orbital paths
const orbits = svg.append("g").attr("class", "orbits");

data.forEach(planet => {
    orbits.append("circle")
        .attr("cx", centerX)
        .attr("cy", centerY)
        .attr("r", planet.distance * scale)
        .attr("fill", "none")
        .attr("stroke", "#333")
        .attr("stroke-width", 0.5)
        .attr("stroke-dasharray", "2,2")
        .attr("opacity", 0.3);
});

// Draw sun
const sun = svg.append("circle")
    .attr("cx", centerX)
    .attr("cy", centerY)
    .attr("r", 20 * scale)
    .attr("fill", "url(#sun-gradient)")
    .style("filter", "url(#glow)");

// Create planet groups
const planetGroups = svg.append("g").attr("class", "planets");

const planets = planetGroups.selectAll(".planet")
    .data(data)
    .enter().append("g")
    .attr("class", "planet");

// Add planets
planets.append("circle")
    .attr("r", d => d.radius * scale)
    .attr("fill", d => d.color)
    .attr("stroke", "#000")
    .attr("stroke-width", 0.5);

// Add planet labels
planets.append("text")
    .attr("dy", d => d.radius * scale + 12)
    .attr("text-anchor", "middle")
    .attr("font-size", "10px")
    .attr("fill", "#666")
    .text(d => d.name);

// Tooltip for planet info
const tooltip = d3.select("body").append("div")
    .attr("class", "d3-tooltip")
    .style("position", "absolute")
    .style("padding", "10px")
    .style("background", "rgba(0,0,0,0.8)")
    .style("color", "white")
    .style("border-radius", "5px")
    .style("pointer-events", "none")
    .style("opacity", 0);

planets.on("mouseover", function(event, d) {
    tooltip.transition().duration(200).style("opacity", .9);
    tooltip.html(`<strong>${d.name}</strong><br/>
                  Orbital Period: ${d.period} Earth years<br/>
                  Distance: ${d.distance} AU (scaled)`)
        .style("left", (event.pageX + 10) + "px")
        .style("top", (event.pageY - 10) + "px");
})
.on("mouseout", function() {
    tooltip.transition().duration(500).style("opacity", 0);
});

// Animation variables
let animationSpeed = 1;
let startTime = Date.now();
let animationId = null;

// Update planet positions
function updatePlanets() {
    const elapsed = (Date.now() - startTime) * 0.001 * animationSpeed;

    planets.attr("transform", d => {
        const angle = (elapsed / d.period) * Math.PI * 2;
        const x = centerX + Math.cos(angle) * d.distance * scale;
        const y = centerY + Math.sin(angle) * d.distance * scale;
        return `translate(${x}, ${y})`;
    });

    animationId = requestAnimationFrame(updatePlanets);
}

// Speed control
const speedControl = svg.append("g")
    .attr("transform", `translate(20, ${height - 40})`);

speedControl.append("text")
    .attr("font-size", "12px")
    .attr("fill", "#666")
    .text("Speed:");

const speeds = [0.1, 0.5, 1, 2, 5, 10];
speeds.forEach((speed, i) => {
    speedControl.append("text")
        .attr("x", 50 + i * 30)
        .attr("font-size", "12px")
        .attr("fill", speed === 1 ? "#4A90E2" : "#666")
        .attr("cursor", "pointer")
        .text(`${speed}x`)
        .on("click", function() {
            animationSpeed = speed;
            speedControl.selectAll("text").attr("fill", "#666");
            d3.select(this).attr("fill", "#4A90E2");
        });
});

// Add title
svg.append("text")
    .attr("x", width / 2)
    .attr("y", 30)
    .attr("text-anchor", "middle")
    .attr("font-size", "20px")
    .attr("font-weight", "bold")
    .attr("fill", "#333")
    .text("☀️ Solar System Orbital Mechanics");

// Start animation
updatePlanets();

// Return control object
return {
    play: () => {
        if (!animationId) {
            startTime = Date.now();
            updatePlanets();
        }
    },
    pause: () => {
        if (animationId) {
            cancelAnimationFrame(animationId);
            animationId = null;
        }
    },
    stop: () => {
        if (animationId) {
            cancelAnimationFrame(animationId);
            animationId = null;
        }
        // Clean up tooltip
        if (tooltip) {
            tooltip.remove();
        }
    }
};
"""

solar_viz = d3_animation(solar_system_code, planets, auto_play=True)
register_d3_visualization(
    solar_viz,
    "solar_system",
    metadata={'title': '🚀 Solar System Simulation'}
)