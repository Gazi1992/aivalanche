export function attachPlotInteractions(plotDiv) {
  if (!plotDiv) return;

  plotDiv.addEventListener('contextmenu', e => e.preventDefault());

  // Check if this is a special plot type that doesn't support zoom/pan
  const isSpecialPlot = checkSpecialPlotType(plotDiv);

  // Skip interaction handlers for special plot types
  if (isSpecialPlot) {
    return;
  }

  if (!plotDiv.__scaleHandlerAttached) {
    plotDiv.__scaleHandlerAttached = true;
    attachScaleHandler(plotDiv);
  }

  if (!plotDiv.__panHandlerAttached) {
    plotDiv.__panHandlerAttached = true;
    attachPanHandler(plotDiv);
  }

  if (!plotDiv.__wheelHandlerAttached) {
    plotDiv.__wheelHandlerAttached = true;
    attachWheelHandler(plotDiv);
  }
}

function checkSpecialPlotType(plotDiv) {
  // First check if we have metadata with explicit plot type
  if (plotDiv.metadata && plotDiv.metadata.plotType) {
    const plotType = plotDiv.metadata.plotType;
    return plotType === 'pie' ||
           plotType === 'scatterpolar' ||
           plotType === 'sankey';
  }

  // Fallback to automatic detection from plot data
  const data = plotDiv.data || plotDiv._fullData;
  if (!data || !data[0]) return false;
  const firstTrace = data[0];
  return firstTrace.type === 'pie' ||
         firstTrace.type === 'scatterpolar' ||
         firstTrace.type === 'sankey';
}

function attachScaleHandler(plotDiv) {
  let startX = 0, startY = 0;
  let initXRange = null, initYRange = null;
  let activeXAxis = 'xaxis';
  let activeYAxis = 'yaxis';
  let rect = null;

  const onPointerMove = (moveEvt) => {
    if (moveEvt.buttons !== 2) return;

    const dx = moveEvt.clientX - startX;
    const dy = moveEvt.clientY - startY;
    const sensitivity = 0.2;
    const factorX = 1 - dx / (rect.width * sensitivity);
    const factorY = 1 + dy / (rect.height * sensitivity);

    const clamp = (val, min, max) => Math.max(min, Math.min(max, val));
    const fx = clamp(factorX, 0.1, 10);
    const fy = clamp(factorY, 0.1, 10);

    if (initXRange && initYRange) {
      const xCenter = (initXRange[0] + initXRange[1]) / 2;
      const xHalf = (initXRange[1] - initXRange[0]) / 2 * fx;
      const yCenter = (initYRange[0] + initYRange[1]) / 2;
      const yHalf = (initYRange[1] - initYRange[0]) / 2 * fy;

      const isXAsc = initXRange[0] < initXRange[1];
      const isYAsc = initYRange[0] < initYRange[1];

      const xMin = xCenter - xHalf;
      const xMax = xCenter + xHalf;
      const yMin = yCenter - yHalf;
      const yMax = yCenter + yHalf;

      const update = {
        [`${activeXAxis}.range`]: isXAsc ? [xMin, xMax] : [xMax, xMin],
        [`${activeYAxis}.range`]: isYAsc ? [yMin, yMax] : [yMax, yMin]
      };

      window.Plotly.relayout(plotDiv, update);
    }
  };

  const onPointerUp = () => {
    window.removeEventListener('pointermove', onPointerMove);
    window.removeEventListener('pointerup', onPointerUp);
  };

  plotDiv.addEventListener('pointerdown', downEvt => {
    if (downEvt.button !== 2) return;
    downEvt.preventDefault();

    rect = plotDiv.getBoundingClientRect();
    startX = downEvt.clientX;
    startY = downEvt.clientY;

    const layout = plotDiv._fullLayout;
    const { activeX, activeY } = findActiveAxes(layout, downEvt, rect);

    activeXAxis = activeX;
    activeYAxis = activeY;

    if (!layout[activeXAxis] || !layout[activeYAxis] ||
        !layout[activeXAxis].range || !layout[activeYAxis].range) {
      console.warn(`Invalid axes selected: ${activeXAxis}, ${activeYAxis}`);
      return;
    }

    initXRange = [...layout[activeXAxis].range];
    initYRange = [...layout[activeYAxis].range];


    window.addEventListener('pointermove', onPointerMove);
    window.addEventListener('pointerup', onPointerUp);
  });
}

function attachPanHandler(plotDiv) {
  let startX = 0, startY = 0;
  let initXRange = null, initYRange = null;
  let activeXAxis = 'xaxis';
  let activeYAxis = 'yaxis';
  let rect = null;

  const onPanMove = (mvEvt) => {
    if ((mvEvt.buttons & 4) === 0) return;

    const dx = mvEvt.clientX - startX;
    const dy = mvEvt.clientY - startY;

    if (initXRange && initYRange) {
      const xScale = (initXRange[1] - initXRange[0]) / rect.width;
      const yScale = (initYRange[1] - initYRange[0]) / rect.height;
      const xOffset = dx * xScale;
      const yOffset = -dy * yScale;

      const newX0 = initXRange[0] - xOffset;
      const newX1 = initXRange[1] - xOffset;
      const newY0 = initYRange[0] - yOffset;
      const newY1 = initYRange[1] - yOffset;

      const update = {
        [`${activeXAxis}.range`]: [newX0, newX1],
        [`${activeYAxis}.range`]: [newY0, newY1]
      };

      window.Plotly.relayout(plotDiv, update);
    }
  };

  const onPanUp = () => {
    window.removeEventListener('pointermove', onPanMove);
    window.removeEventListener('pointerup', onPanUp);
  };

  plotDiv.addEventListener('pointerdown', (pdEvt) => {
    if (pdEvt.button !== 1) return;
    pdEvt.preventDefault();

    rect = plotDiv.getBoundingClientRect();
    startX = pdEvt.clientX;
    startY = pdEvt.clientY;

    const layout = plotDiv._fullLayout;
    const { activeX, activeY } = findActiveAxes(layout, pdEvt, rect);

    activeXAxis = activeX;
    activeYAxis = activeY;

    if (!layout[activeXAxis] || !layout[activeYAxis] ||
        !layout[activeXAxis].range || !layout[activeYAxis].range) {
      console.warn(`Invalid axes selected: ${activeXAxis}, ${activeYAxis}`);
      return;
    }

    initXRange = [...layout[activeXAxis].range];
    initYRange = [...layout[activeYAxis].range];


    window.addEventListener('pointermove', onPanMove);
    window.addEventListener('pointerup', onPanUp);
  });
}

function findActiveAxes(layout, event, rect) {
  const relX = (event.clientX - rect.left) / rect.width;
  const relY = 1 - (event.clientY - rect.top) / rect.height;


  const xAxes = Object.keys(layout).filter(k => k.startsWith('xaxis'));

  let activeX = 'xaxis';
  let activeY = 'yaxis';
  let bestMatch = null;
  let smallestArea = Infinity;

  const sortedAxes = xAxes.sort((a, b) => {
    const aNum = a === 'xaxis' ? 0 : parseInt(a.replace('xaxis', ''));
    const bNum = b === 'xaxis' ? 0 : parseInt(b.replace('xaxis', ''));
    return bNum - aNum;
  });

  for (const xName of sortedAxes) {
    const yName = xName.replace('xaxis', 'yaxis');
    const xAxis = layout[xName];
    const yAxis = layout[yName];

    if (xAxis && yAxis && xAxis.domain && yAxis.domain) {
      if (relX >= xAxis.domain[0] && relX <= xAxis.domain[1] &&
          relY >= yAxis.domain[0] && relY <= yAxis.domain[1]) {

        const area = (xAxis.domain[1] - xAxis.domain[0]) * (yAxis.domain[1] - yAxis.domain[0]);


        if (area < smallestArea) {
          smallestArea = area;
          bestMatch = { activeX: xName, activeY: yName };
        }
      }
    }
  }

  if (bestMatch) {
    activeX = bestMatch.activeX;
    activeY = bestMatch.activeY;
  }

  return { activeX, activeY };
}


function attachWheelHandler(plotDiv) {
  const ZOOM_SENSITIVITY = 0.2;

  const handleWheel = (event) => {
    if (event.shiftKey) return;

    event.preventDefault();

    const rect = plotDiv.getBoundingClientRect();
    const layout = plotDiv._fullLayout;
    if (!layout) return;

    const { activeX, activeY } = findActiveAxes(layout, event, rect);

    const xAxis = layout[activeX];
    const yAxis = layout[activeY];

    if (!xAxis || !yAxis || !xAxis.range || !yAxis.range) return;

    const relX = (event.clientX - rect.left) / rect.width;
    const relY = 1 - (event.clientY - rect.top) / rect.height;

    const xRatio = (relX - xAxis.domain[0]) / (xAxis.domain[1] - xAxis.domain[0]);
    const yRatio = (relY - yAxis.domain[0]) / (yAxis.domain[1] - yAxis.domain[0]);

    const delta = event.deltaY > 0 ? -ZOOM_SENSITIVITY : ZOOM_SENSITIVITY;
    const factor = 1 + delta;

    const xRange = xAxis.range;
    const yRange = yAxis.range;

    const xCenter = xRange[0] + xRatio * (xRange[1] - xRange[0]);
    const yCenter = yRange[0] + yRatio * (yRange[1] - yRange[0]);

    const newXRange = [
      xCenter - (xCenter - xRange[0]) * factor,
      xCenter + (xRange[1] - xCenter) * factor
    ];
    const newYRange = [
      yCenter - (yCenter - yRange[0]) * factor,
      yCenter + (yRange[1] - yCenter) * factor
    ];

    const update = {};
    update[`${activeX}.range`] = newXRange;
    update[`${activeY}.range`] = newYRange;

    Plotly.relayout(plotDiv, update);
  };

  plotDiv.addEventListener('wheel', handleWheel, { passive: false });
}