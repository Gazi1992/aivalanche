import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as d3 from 'd3';
import * as topojson from 'topojson-client';
import PlotButton from '../PlotButton';
import {
  EditIcon,
  TableIcon,
  ExpandIcon,
  ShrinkIcon,
  DownloadIcon,
  PlayIcon,
  PauseIcon,
  RestartIcon,
  GifIcon
} from '../icons';
import './D3Container.css';

/**
 * D3Container Component
 * Renders D3.js visualizations with maximum flexibility
 * Executes D3 code provided from Python backend
 */
const D3Container = ({
  figure,
  vizId,
  onInteraction,
  onEdit,
  onViewTable,
  onExpand,
  isExpanded = false,
  showExpandButton = true
}) => {
  const svgRef = useRef(null);
  const containerRef = useRef(null);
  const animationRef = useRef(null);
  const [isAnimating, setIsAnimating] = useState(false);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [error, setError] = useState(null);
  const [isExportingGif, setIsExportingGif] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);
  const frameDataRef = useRef([]);

  // Parse the D3 configuration
  const config = figure?.d3Config || {};
  const metadata = figure?.metadata || {};

  // Check if this is an animation
  const isAnimation = config?.isAnimation || metadata?.isAnimation || false;

  // Update dimensions based on container size
  useEffect(() => {
    if (!containerRef.current) return;

    const updateDimensions = () => {
      const { width, height } = containerRef.current.getBoundingClientRect();
      // Use full container size for D3 visualizations
      setDimensions({
        width: Math.max(width, 300),
        height: Math.max(height, 300)
      });
    };

    updateDimensions();

    // Use ResizeObserver for better resize detection
    const resizeObserver = new ResizeObserver(updateDimensions);
    resizeObserver.observe(containerRef.current);

    return () => resizeObserver.disconnect();
  }, []);

  // Execute D3 visualization code on mount or when config/dimensions change
  useEffect(() => {
    if (!svgRef.current || !config) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();
    setError(null);

    // Always use container dimensions for proper scaling
    const width = dimensions.width;
    const height = dimensions.height;

    svg.attr('width', width)
       .attr('height', height);

    try {
      const data = config.data || null;
      const vizType = config.type || 'custom';

      if (config.code) {
        // The code should directly return the control object, not wrapped in IIFE
        const executeD3 = new Function(
          'svg', 'data', 'width', 'height', 'd3', 'topojson',
          config.code
        );

        const result = executeD3(svg, data, width, height, d3, topojson);

        // Store animation controls if returned
        console.log('D3 execution result:', result, 'Type:', typeof result);
        if (result && typeof result === 'object') {
          animationRef.current = result;
          console.log('Stored animation controls:', animationRef.current);
          // Auto-play if animation has a play method and autoPlay is true
          if (result.play && config.autoPlay === true) {
            console.log('Auto-playing animation');
            result.play();
            setIsAnimating(true);
          }
        } else if (typeof result === 'function') {
          // Legacy support: if a function is returned, treat it as a stop function
          animationRef.current = { stop: result };
        }
      } else {
        switch (vizType) {
          case 'force':
            renderForceGraph(svg, data, width, height);
            break;
          case 'hierarchy':
            renderHierarchy(svg, data, config.layout || 'tree', width, height);
            break;
          default:
            console.warn(`No code provided for D3 visualization type: ${vizType}`);
        }
      }
    } catch (err) {
      console.error('Error executing D3 code:', err);
      setError(err.message);

      svg.append('text')
        .attr('x', dimensions.width / 2)
        .attr('y', dimensions.height / 2)
        .attr('text-anchor', 'middle')
        .attr('fill', 'red')
        .text(`Error: ${err.message}`);
    }

    // Cleanup function
    return () => {
      if (animationRef.current?.stop) {
        animationRef.current.stop();
      }
      animationRef.current = null;
      if (svgRef.current) {
        const svg = d3.select(svgRef.current);
        svg.selectAll('*').remove();
      }
    };
  }, [config, dimensions]);

  // Render force-directed graph (fallback for when no code is provided)
  const renderForceGraph = (svg, data, width, height) => {
    if (!data || !data.nodes) return;

    const simulation = d3.forceSimulation(data.nodes)
      .force('link', d3.forceLink(data.links || [])
        .id(d => d.id)
        .distance(50))
      .force('charge', d3.forceManyBody().strength(-100))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(d => d.radius || 5));

    const link = svg.append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(data.links || [])
      .enter().append('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', d => Math.sqrt(d.value || 1));

    const node = svg.append('g')
      .attr('class', 'nodes')
      .selectAll('circle')
      .data(data.nodes)
      .enter().append('circle')
      .attr('r', d => d.radius || 5)
      .attr('fill', d => d.color || '#69b3a2')
      .call(drag(simulation));

    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);
    });

    animationRef.current = simulation;
  };

  // Render hierarchy (fallback)
  const renderHierarchy = (svg, data, layout, width, height) => {
    if (!data) return;

    const root = d3.hierarchy(data);
    const margin = { top: 20, right: 20, bottom: 20, left: 20 };

    let layoutFunc;
    switch (layout) {
      case 'tree':
        layoutFunc = d3.tree().size([width - margin.left - margin.right, height - margin.top - margin.bottom]);
        break;
      case 'cluster':
        layoutFunc = d3.cluster().size([width - margin.left - margin.right, height - margin.top - margin.bottom]);
        break;
      case 'treemap':
        layoutFunc = d3.treemap().size([width, height]).padding(2);
        root.sum(d => d.value || 1);
        break;
      case 'pack':
        layoutFunc = d3.pack().size([width, height]).padding(3);
        root.sum(d => d.value || 1);
        break;
      default:
        layoutFunc = d3.tree().size([width - margin.left - margin.right, height - margin.top - margin.bottom]);
    }

    layoutFunc(root);

    if (layout === 'tree' || layout === 'cluster') {
      const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

      g.selectAll('.link')
        .data(root.links())
        .enter().append('path')
        .attr('class', 'link')
        .attr('d', d3.linkVertical()
          .x(d => d.x)
          .y(d => d.y))
        .attr('fill', 'none')
        .attr('stroke', '#555')
        .attr('stroke-width', 1.5);

      const node = g.selectAll('.node')
        .data(root.descendants())
        .enter().append('g')
        .attr('class', 'node')
        .attr('transform', d => `translate(${d.x},${d.y})`);

      node.append('circle')
        .attr('r', 5)
        .attr('fill', d => d.children ? '#555' : '#999');

      node.append('text')
        .attr('dy', '0.31em')
        .attr('x', d => d.children ? -10 : 10)
        .style('text-anchor', d => d.children ? 'end' : 'start')
        .text(d => d.data.name);
    }
  };

  // Helper: Drag behavior
  const drag = simulation => {
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

    return d3.drag()
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended);
  };

  // Control handlers
  const handleRestart = () => {
    if (!svgRef.current || !config) return;

    // Clean up any existing animations
    if (animationRef.current?.stop) {
      animationRef.current.stop();
    }
    animationRef.current = null;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();
    setError(null);

    // Always use container dimensions for proper scaling
    const width = dimensions.width;
    const height = dimensions.height;

    svg.attr('width', width)
       .attr('height', height);

    try {
      const data = config.data || null;
      const vizType = config.type || 'custom';

      if (config.code) {
        // The code should directly return the control object, not wrapped in IIFE
        const executeD3 = new Function(
          'svg', 'data', 'width', 'height', 'd3', 'topojson',
          config.code
        );

        const result = executeD3(svg, data, width, height, d3, topojson);

        // Store animation controls if returned
        console.log('D3 execution result:', result, 'Type:', typeof result);
        if (result && typeof result === 'object') {
          animationRef.current = result;
          console.log('Stored animation controls:', animationRef.current);
          // Auto-play if animation has a play method and autoPlay is true
          if (result.play && config.autoPlay === true) {
            console.log('Auto-playing animation');
            result.play();
            setIsAnimating(true);
          }
        } else if (typeof result === 'function') {
          // Legacy support: if a function is returned, treat it as a stop function
          animationRef.current = { stop: result };
        }
      } else {
        switch (vizType) {
          case 'force':
            renderForceGraph(svg, data, width, height);
            break;
          case 'hierarchy':
            renderHierarchy(svg, data, config.layout || 'tree', width, height);
            break;
          default:
            console.warn(`No code provided for D3 visualization type: ${vizType}`);
        }
      }
    } catch (err) {
      console.error('Error executing D3 code:', err);
      setError(err.message);

      svg.append('text')
        .attr('x', dimensions.width / 2)
        .attr('y', dimensions.height / 2)
        .attr('text-anchor', 'middle')
        .attr('fill', 'red')
        .text(`Error: ${err.message}`);
    }
  };

  const handleDownload = () => {
    if (!svgRef.current) return;

    // Serialize SVG to string
    const serializer = new XMLSerializer();
    const svgString = serializer.serializeToString(svgRef.current);

    // Create blob and download
    const blob = new Blob([svgString], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${vizId || 'd3-viz'}.svg`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Animation control handlers
  const handlePlayPause = () => {
    console.log('Play/Pause clicked. Current animationRef:', animationRef.current);
    console.log('isAnimating:', isAnimating);

    if (!animationRef.current) {
      console.error('No animation controls available');
      return;
    }

    if (isAnimating) {
      // Pause animation
      console.log('Pausing animation');
      if (animationRef.current.pause) {
        animationRef.current.pause();
      }
      setIsAnimating(false);
    } else {
      // Play animation
      console.log('Playing animation');
      if (animationRef.current.play) {
        animationRef.current.play();
      } else {
        console.error('No play method found on animationRef.current');
      }
      setIsAnimating(true);
    }
  };

  const handleExportGif = async () => {
    if (!svgRef.current) return;

    setIsExportingGif(true);
    setExportProgress(0);

    try {
      // If the D3 code provided a captureFrames function, use it
      if (animationRef.current?.captureFrames) {
        const frames = await animationRef.current.captureFrames((progress) => {
          setExportProgress(Math.round(progress * 100));
        });

        // Convert frames to GIF
        if (frames && frames.length > 0) {
          const gifData = await createGifFromFrames(frames);
          downloadGifData(gifData, `${vizId || 'd3-animation'}.gif`);
        }
      } else if (animationRef.current?.getFrameCount) {
        // Alternative: If animation provides frame count, capture frames manually
        const frameCount = animationRef.current.getFrameCount();
        const frames = [];

        // Stop current animation if playing
        const wasPlaying = isAnimating;
        if (wasPlaying && animationRef.current.pause) {
          animationRef.current.pause();
        }

        // Capture each frame
        for (let i = 0; i < frameCount; i++) {
          if (animationRef.current.setFrame) {
            animationRef.current.setFrame(i);
            await new Promise(resolve => setTimeout(resolve, 50)); // Wait for render

            // Capture current SVG state
            const svgElement = svgRef.current;
            const svgData = new XMLSerializer().serializeToString(svgElement);
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();

            canvas.width = dimensions.width;
            canvas.height = dimensions.height;

            // Convert SVG to image
            const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
            const url = URL.createObjectURL(svgBlob);

            await new Promise((resolve, reject) => {
              img.onload = () => {
                ctx.fillStyle = 'white';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(img, 0, 0);
                frames.push(canvas.toDataURL('image/png'));
                URL.revokeObjectURL(url);
                resolve();
              };
              img.onerror = reject;
              img.src = url;
            });

            setExportProgress(Math.round((i + 1) / frameCount * 100));
          }
        }

        // Create and download GIF
        if (frames.length > 0) {
          const gifData = await createGifFromFrames(frames);
          downloadGifData(gifData, `${vizId || 'd3-animation'}.gif`);
        }

        // Resume animation if it was playing
        if (wasPlaying && animationRef.current.play) {
          animationRef.current.play();
        }
      } else {
        console.warn('Animation does not provide frame capture capabilities');
      }
    } catch (err) {
      console.error('Error exporting GIF:', err);
    } finally {
      setIsExportingGif(false);
      setExportProgress(0);
    }
  };

  // Helper function for GIF creation
  const createGifFromFrames = async (frames) => {
    // Dynamic import of gif.js library
    const GIF = (await import('gif.js')).default;

    return new Promise(async (resolve, reject) => {
      const gif = new GIF({
        workers: 2,
        quality: 10,
        width: dimensions.width,
        height: dimensions.height,
        workerScript: '/gif.worker.js'
      });

      // Convert SVG strings to images and add to GIF
      for (let i = 0; i < frames.length; i++) {
        const frame = frames[i];

        // Check if frame is an SVG string or already a data URL
        if (frame.startsWith('<svg') || frame.startsWith('<?xml')) {
          // Convert SVG string to image
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');
          const img = new Image();

          canvas.width = dimensions.width;
          canvas.height = dimensions.height;

          const svgBlob = new Blob([frame], { type: 'image/svg+xml;charset=utf-8' });
          const url = URL.createObjectURL(svgBlob);

          await new Promise((imgResolve, imgReject) => {
            img.onload = () => {
              ctx.fillStyle = 'white';
              ctx.fillRect(0, 0, canvas.width, canvas.height);
              ctx.drawImage(img, 0, 0);
              gif.addFrame(canvas, { delay: 100, copy: true });
              URL.revokeObjectURL(url);
              imgResolve();
            };
            img.onerror = imgReject;
            img.src = url;
          });
        } else {
          // Frame is already a data URL or image
          const img = new Image();
          img.src = frame;
          gif.addFrame(img, { delay: 100 });
        }
      }

      gif.on('finished', (blob) => {
        resolve(blob);
      });

      gif.on('error', reject);

      gif.render();
    });
  };

  const downloadGifData = (blob, filename) => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div ref={containerRef} className="d3-container" style={{
      width: '100%',
      height: '100%',
      position: 'relative',
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* Control buttons - positioned absolute top-right like PlotContainer */}
      <div className="plot-buttons" style={{
        position: 'absolute',
        top: '4px',
        right: '4px',
        display: 'flex',
        gap: '4px',
        zIndex: 10
      }}>
        {/* Animation controls (if this is an animation) */}
        {isAnimation && (
          <>
            <PlotButton
              onClick={handlePlayPause}
              title={isAnimating ? "Pause" : "Play"}
              icon={isAnimating ? PauseIcon : PlayIcon}
            />
            <PlotButton
              onClick={handleExportGif}
              title={isExportingGif ? `Exporting... ${exportProgress}%` : "Export as GIF"}
              icon={GifIcon}
              disabled={isExportingGif}
              style={isExportingGif ? { opacity: 0.6 } : {}}
            />
            {/* Add separator between animation and regular buttons */}
            <div className="plot-button-separator" style={{
              width: '1px',
              backgroundColor: '#ccc',
              margin: '0 4px',
              alignSelf: 'stretch'
            }} />
          </>
        )}

        <PlotButton
          onClick={handleRestart}
          title="Restart"
          icon={RestartIcon}
        />

        {onEdit && (
          <PlotButton
            onClick={onEdit}
            title="Edit"
            icon={EditIcon}
          />
        )}

        <PlotButton
          onClick={handleDownload}
          title="Download SVG"
          icon={DownloadIcon}
        />

        {showExpandButton && onExpand && (
          <PlotButton
            onClick={onExpand}
            title={isExpanded ? "Collapse" : "Expand"}
            icon={isExpanded ? ShrinkIcon : ExpandIcon}
          />
        )}
      </div>

      {/* D3 SVG container - takes full space */}
      <div className="d3-viz-container" style={{
        width: '100%',
        height: '100%',
        overflow: 'hidden',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        {error && (
          <div style={{ color: 'red', padding: '10px', position: 'absolute' }}>
            Error: {error}
          </div>
        )}
        <svg ref={svgRef} style={{ display: 'block' }} />
      </div>
    </div>
  );
};

export default D3Container;