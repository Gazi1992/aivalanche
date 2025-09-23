"""
D3.js Animations Demo
Demonstrates animated D3 visualizations with control methods
"""

import json
import random

# Demo 1: Animated bouncing balls
bouncing_balls_code = """
// Set up initial state
const numBalls = 20;
const balls = Array.from({length: numBalls}, (_, i) => ({
  x: Math.random() * width,
  y: Math.random() * height,
  vx: (Math.random() - 0.5) * 4,
  vy: (Math.random() - 0.5) * 4,
  r: Math.random() * 20 + 10,
  color: d3.schemeCategory10[i % 10]
}));

// Create circles
const circles = svg.selectAll('circle')
  .data(balls)
  .enter().append('circle')
  .attr('r', d => d.r)
  .attr('fill', d => d.color)
  .attr('fill-opacity', 0.7)
  .attr('stroke', '#fff')
  .attr('stroke-width', 2);

// Animation variables
let animationId = null;
let isPaused = false;

// Animation loop
function animate() {
  if (isPaused) return;

  balls.forEach(ball => {
    // Update positions
    ball.x += ball.vx;
    ball.y += ball.vy;

    // Bounce off walls
    if (ball.x - ball.r < 0 || ball.x + ball.r > width) {
      ball.vx = -ball.vx;
      ball.x = Math.max(ball.r, Math.min(width - ball.r, ball.x));
    }
    if (ball.y - ball.r < 0 || ball.y + ball.r > height) {
      ball.vy = -ball.vy;
      ball.y = Math.max(ball.r, Math.min(height - ball.r, ball.y));
    }
  });

  // Update circle positions
  circles
    .attr('cx', d => d.x)
    .attr('cy', d => d.y);

  animationId = requestAnimationFrame(animate);
}

// Return control methods
return {
  play: () => {
    isPaused = false;
    if (!animationId) animate();
  },
  pause: () => {
    isPaused = true;
  },
  stop: () => {
    isPaused = true;
    if (animationId) {
      cancelAnimationFrame(animationId);
      animationId = null;
    }
  }
};
"""

bouncing_viz = create_d3_viz(bouncing_balls_code, None, viz_type='animation')
bouncing_viz['isAnimation'] = True
bouncing_viz['autoPlay'] = True
register_d3_visualization(bouncing_viz, "bouncing_balls",
                         metadata={"title": "Bouncing Balls Animation"})


# Demo 2: Animated spiral
spiral_code = """
// Spiral parameters
let angle = 0;
let radius = 0;
const centerX = width / 2;
const centerY = height / 2;
const maxRadius = Math.min(width, height) * 0.4;

// Create path
const path = svg.append('path')
  .attr('fill', 'none')
  .attr('stroke', '#4a90e2')
  .attr('stroke-width', 2);

// Create trailing circle
const circle = svg.append('circle')
  .attr('r', 5)
  .attr('fill', '#e24a90')
  .attr('stroke', '#fff')
  .attr('stroke-width', 2);

// Path data accumulator
let pathData = [];
let animationId = null;
let isPaused = false;

// Animation function
function animateSpiral() {
  if (isPaused) return;

  // Update spiral
  angle += 0.1;
  radius = (angle / (Math.PI * 10)) * maxRadius;

  if (radius > maxRadius) {
    // Reset spiral
    angle = 0;
    radius = 0;
    pathData = [];
  }

  const x = centerX + radius * Math.cos(angle);
  const y = centerY + radius * Math.sin(angle);

  // Add to path
  pathData.push([x, y]);
  if (pathData.length > 500) {
    pathData.shift(); // Limit trail length
  }

  // Update path
  const line = d3.line();
  path.attr('d', line(pathData));

  // Update circle position
  circle.attr('cx', x).attr('cy', y);

  animationId = requestAnimationFrame(animateSpiral);
}

// Return control methods
return {
  play: () => {
    isPaused = false;
    if (!animationId) animateSpiral();
  },
  pause: () => {
    isPaused = true;
  },
  stop: () => {
    isPaused = true;
    if (animationId) {
      cancelAnimationFrame(animationId);
      animationId = null;
    }
    // Clear the visualization
    pathData = [];
    path.attr('d', '');
    angle = 0;
    radius = 0;
  }
};
"""

spiral_viz = create_d3_viz(spiral_code, None, viz_type='animation')
spiral_viz['isAnimation'] = True
spiral_viz['autoPlay'] = False  # Don't auto-play this one
register_d3_visualization(spiral_viz, "spiral_animation",
                         metadata={"title": "Animated Spiral"})


# Demo 3: Animated force graph
force_nodes = [{"id": i, "group": i % 3} for i in range(30)]
force_links = []
for i in range(30):
    for j in range(i + 1, min(i + 3, 30)):
        force_links.append({"source": i, "target": j})

animated_force_code = """
// Create simulation
const simulation = d3.forceSimulation(data.nodes)
  .force("link", d3.forceLink(data.links).id(d => d.id).distance(50))
  .force("charge", d3.forceManyBody().strength(-100))
  .force("center", d3.forceCenter(width / 2, height / 2))
  .force("collision", d3.forceCollide().radius(10));

// Create links
const link = svg.append("g")
  .selectAll("line")
  .data(data.links)
  .enter().append("line")
  .attr("stroke", "#999")
  .attr("stroke-opacity", 0.6)
  .attr("stroke-width", 2);

// Create nodes
const node = svg.append("g")
  .selectAll("circle")
  .data(data.nodes)
  .enter().append("circle")
  .attr("r", 8)
  .attr("fill", d => d3.schemeCategory10[d.group])
  .attr("stroke", "#fff")
  .attr("stroke-width", 2);

// Add drag behavior
node.call(d3.drag()
  .on("start", dragstarted)
  .on("drag", dragged)
  .on("end", dragended));

// Update positions on tick
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

// Periodic force changes for animation
let forceInterval = null;

function animateForces() {
  const timer = d3.interval(() => {
    // Randomly change force strengths
    simulation
      .force("charge")
      .strength(-50 - Math.random() * 200);

    simulation.alpha(0.3).restart();
  }, 2000);

  return timer;
}

// Start animation
forceInterval = animateForces();

// Return control methods
return {
  play: () => {
    if (!forceInterval) {
      forceInterval = animateForces();
    }
    simulation.alpha(0.3).restart();
  },
  pause: () => {
    if (forceInterval) {
      forceInterval.stop();
      forceInterval = null;
    }
    simulation.stop();
  },
  stop: () => {
    if (forceInterval) {
      forceInterval.stop();
      forceInterval = null;
    }
    simulation.stop();
    simulation.alpha(0);
  }
};
"""

force_viz = create_d3_viz(animated_force_code,
                         {"nodes": force_nodes, "links": force_links},
                         viz_type='animation')
force_viz['isAnimation'] = True
force_viz['autoPlay'] = True
register_d3_visualization(force_viz, "animated_force",
                         metadata={"title": "Animated Force Layout"})


# Demo 4: Wave animation
wave_code = """
// Wave parameters
const numPoints = 100;
const amplitude = height / 4;
const frequency = 0.02;
let phase = 0;

// Generate initial points
function generateWavePoints() {
  const points = [];
  for (let i = 0; i <= numPoints; i++) {
    const x = (i / numPoints) * width;
    const y = height / 2 + amplitude * Math.sin(frequency * x + phase);
    points.push([x, y]);
  }
  return points;
}

// Create gradient
const gradient = svg.append("defs")
  .append("linearGradient")
  .attr("id", "wave-gradient")
  .attr("x1", "0%")
  .attr("y1", "0%")
  .attr("x2", "0%")
  .attr("y2", "100%");

gradient.append("stop")
  .attr("offset", "0%")
  .attr("stop-color", "#4a90e2")
  .attr("stop-opacity", 0.8);

gradient.append("stop")
  .attr("offset", "100%")
  .attr("stop-color", "#4a90e2")
  .attr("stop-opacity", 0.2);

// Create area generator
const area = d3.area()
  .x(d => d[0])
  .y0(height)
  .y1(d => d[1])
  .curve(d3.curveMonotoneX);

// Create path
const wavePath = svg.append("path")
  .attr("fill", "url(#wave-gradient)")
  .attr("stroke", "#4a90e2")
  .attr("stroke-width", 2);

// Animation variables
let animationId = null;
let isPaused = false;

// Animation loop
function animateWave() {
  if (isPaused) return;

  phase += 0.05;
  const points = generateWavePoints();
  wavePath.attr("d", area(points));

  animationId = requestAnimationFrame(animateWave);
}

// Start animation
animateWave();

// Return control methods
return {
  play: () => {
    isPaused = false;
    if (!animationId) animateWave();
  },
  pause: () => {
    isPaused = true;
  },
  stop: () => {
    isPaused = true;
    if (animationId) {
      cancelAnimationFrame(animationId);
      animationId = null;
    }
    phase = 0;
    const points = generateWavePoints();
    wavePath.attr("d", area(points));
  }
};
"""

wave_viz = create_d3_viz(wave_code, None, viz_type='animation')
wave_viz['isAnimation'] = True
wave_viz['autoPlay'] = True
register_d3_visualization(wave_viz, "wave_animation",
                         metadata={"title": "Wave Animation"})

print("D3 animations demo created with 4 animated visualizations")