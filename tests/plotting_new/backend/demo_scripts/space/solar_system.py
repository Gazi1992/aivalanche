"""
Solar System Animation
Interactive animated visualization of the solar system
"""

# Solar System Animation D3 Code
solar_system_code = """
// Solar System Animation with orbiting planets
const centerX = width / 2;
const centerY = height / 2;
// Scale to fit the container properly - Neptune's orbit is 350, so we need at least 700 + padding
const maxOrbitRadius = 350;
const padding = 20; // Leave some padding around the edges
const scale = Math.min(width - padding * 2, height - padding * 2) / (maxOrbitRadius * 2 + 40);

// Planet data with orbital parameters
const planets = [
    {name: 'Mercury', radius: 3, orbitRadius: 50, color: '#8C7853', period: 2000},
    {name: 'Venus', radius: 5, orbitRadius: 75, color: '#FFC649', period: 3000},
    {name: 'Earth', radius: 5, orbitRadius: 100, color: '#4169E1', period: 4000},
    {name: 'Mars', radius: 4, orbitRadius: 130, color: '#CD5C5C', period: 5000},
    {name: 'Jupiter', radius: 12, orbitRadius: 200, color: '#DAA520', period: 8000},
    {name: 'Saturn', radius: 10, orbitRadius: 250, color: '#F4A460', period: 10000},
    {name: 'Uranus', radius: 7, orbitRadius: 300, color: '#4FD0E0', period: 12000},
    {name: 'Neptune', radius: 7, orbitRadius: 350, color: '#4169FF', period: 14000}
];

// Clear SVG
svg.selectAll('*').remove();

// Create background
svg.append('rect')
    .attr('width', width)
    .attr('height', height)
    .attr('fill', '#000014');

// Add stars
const stars = d3.range(200).map(() => ({
    x: Math.random() * width,
    y: Math.random() * height,
    r: Math.random() * 2
}));

svg.selectAll('.star')
    .data(stars)
    .enter().append('circle')
    .attr('class', 'star')
    .attr('cx', d => d.x)
    .attr('cy', d => d.y)
    .attr('r', d => d.r)
    .attr('fill', 'white')
    .attr('opacity', d => 0.3 + Math.random() * 0.7);

// Create group for solar system
const solarSystem = svg.append('g')
    .attr('transform', `translate(${centerX}, ${centerY}) scale(${scale})`);

// Draw orbits
const orbits = solarSystem.selectAll('.orbit')
    .data(planets)
    .enter().append('circle')
    .attr('class', 'orbit')
    .attr('cx', 0)
    .attr('cy', 0)
    .attr('r', d => d.orbitRadius)
    .attr('fill', 'none')
    .attr('stroke', 'rgba(255, 255, 255, 0.2)')
    .attr('stroke-width', 0.5);

// Draw Sun
const sun = solarSystem.append('circle')
    .attr('cx', 0)
    .attr('cy', 0)
    .attr('r', 15)
    .attr('fill', '#FDB813')
    .attr('filter', 'url(#glow)');

// Add glow effect for sun
const defs = svg.append('defs');
const filter = defs.append('filter')
    .attr('id', 'glow');
filter.append('feGaussianBlur')
    .attr('stdDeviation', '3')
    .attr('result', 'coloredBlur');
const feMerge = filter.append('feMerge');
feMerge.append('feMergeNode')
    .attr('in', 'coloredBlur');
feMerge.append('feMergeNode')
    .attr('in', 'SourceGraphic');

// Create planet groups
const planetGroups = solarSystem.selectAll('.planet-group')
    .data(planets)
    .enter().append('g')
    .attr('class', 'planet-group');

// Add planets
const planetCircles = planetGroups.append('circle')
    .attr('class', 'planet')
    .attr('r', d => d.radius)
    .attr('fill', d => d.color)
    .attr('cx', d => d.orbitRadius)
    .attr('cy', 0);

// Add planet labels
const labels = planetGroups.append('text')
    .attr('class', 'planet-label')
    .attr('x', d => d.orbitRadius)
    .attr('y', d => -d.radius - 5)
    .attr('text-anchor', 'middle')
    .attr('fill', 'white')
    .attr('font-size', '10px')
    .attr('opacity', 0.8)
    .text(d => d.name);

// Animation variables
let animationId = null;
let isPaused = false;
let startTime = Date.now();

// Animation function
function animate() {
    if (!isPaused) {
        const elapsed = Date.now() - startTime;

        planetGroups.attr('transform', d => {
            const angle = (elapsed / d.period) * 2 * Math.PI;
            return `rotate(${angle * 180 / Math.PI})`;
        });

        // Keep labels upright
        labels.attr('transform', d => {
            const angle = (elapsed / d.period) * 2 * Math.PI;
            return `rotate(${-angle * 180 / Math.PI})`;
        });

        animationId = requestAnimationFrame(animate);
    }
}

// Start animation
animate();

// Return control interface
return {
    play: () => {
        isPaused = false;
        animate();
    },
    pause: () => {
        isPaused = true;
        if (animationId) {
            cancelAnimationFrame(animationId);
        }
    },
    stop: () => {
        isPaused = true;
        if (animationId) {
            cancelAnimationFrame(animationId);
        }
        startTime = Date.now();
        planetGroups.attr('transform', 'rotate(0)');
    }
};
"""

# Create and register the solar system animation
solar_system = d3_animation(solar_system_code, data=None, auto_play=True)
register_d3_visualization(solar_system, 'solar_system_animation')