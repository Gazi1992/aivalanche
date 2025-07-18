import React, { useState, useEffect, useRef } from 'react';
import AppearanceSection from './AppearanceSection';
import DataSection from './DataSection';
import { 
  overlayStyle, 
  headerStyle, 
  contentStyle,
  closeButtonStyle,
  backdropStyle 
} from './styles';

const EditPane = ({ isOpen, onClose, plotData, metadata, onUpdate }) => {
  const [appearanceExpanded, setAppearanceExpanded] = useState(true);
  const [dataExpanded, setDataExpanded] = useState(false);
  
  // Title state
  const [titleExpanded, setTitleExpanded] = useState(false);
  const [titleVisible, setTitleVisible] = useState(true);
  const [titleText, setTitleText] = useState('');
  
  // X-axis state
  const [xAxisExpanded, setXAxisExpanded] = useState(false);
  const [xAxisLabelVisible, setXAxisLabelVisible] = useState(true);
  const [xAxisLabel, setXAxisLabel] = useState('');
  const [xAxisScale, setXAxisScale] = useState('linear');
  const [xAxisTicksVisible, setXAxisTicksVisible] = useState(true);
  const [xAxisMin, setXAxisMin] = useState('');
  const [xAxisMax, setXAxisMax] = useState('');
  const [xAxisInverted, setXAxisInverted] = useState(false);
  
  // Y-axis state
  const [yAxisExpanded, setYAxisExpanded] = useState(false);
  const [yAxisLabelVisible, setYAxisLabelVisible] = useState(true);
  const [yAxisLabel, setYAxisLabel] = useState('');
  const [yAxisScale, setYAxisScale] = useState('linear');
  const [yAxisTicksVisible, setYAxisTicksVisible] = useState(true);
  const [yAxisMin, setYAxisMin] = useState('');
  const [yAxisMax, setYAxisMax] = useState('');
  const [yAxisInverted, setYAxisInverted] = useState(false);
  
  // Legend state
  const [legendExpanded, setLegendExpanded] = useState(false);
  const [legendVisible, setLegendVisible] = useState(true);
  const [legendItems, setLegendItems] = useState([]);
  
  const isInitialMount = useRef(true);
  const updateTimer = useRef(null);
  
  // Use metadata to determine plot capabilities
  const hasAxes = metadata?.hasAxes !== false;
  const hasLegend = !metadata?.isPcp && !metadata?.isSplom;

  // Reset subsection states when edit pane is opened
  useEffect(() => {
    if (isOpen) {
      setTitleExpanded(false);
      setXAxisExpanded(false);
      setYAxisExpanded(false);
      setLegendExpanded(false);
    }
  }, [isOpen]);

  // Update state when plotData changes (when a new plot is selected for editing)
  useEffect(() => {
    if (plotData?.layout) {
      const layout = plotData.layout;
      
      // Set title visibility and text
      const hasTitle = layout.title?.text && layout.title.text.trim() !== '';
      setTitleVisible(hasTitle);
      setTitleText(layout.title?.text || '');
      
      // Set x-axis properties
      const hasXLabel = layout.xaxis?.title?.text && layout.xaxis.title.text.trim() !== '';
      setXAxisLabelVisible(hasXLabel);
      setXAxisLabel(layout.xaxis?.title?.text || '');
      setXAxisScale(layout.xaxis?.type || 'linear');
      setXAxisTicksVisible(layout.xaxis?.showticklabels !== false);
      setXAxisMin(layout.xaxis?.range?.[0]?.toString() || '');
      setXAxisMax(layout.xaxis?.range?.[1]?.toString() || '');
      setXAxisInverted(layout.xaxis?.autorange === 'reversed');
      
      // Set y-axis properties
      const hasYLabel = layout.yaxis?.title?.text && layout.yaxis.title.text.trim() !== '';
      setYAxisLabelVisible(hasYLabel);
      setYAxisLabel(layout.yaxis?.title?.text || '');
      setYAxisScale(layout.yaxis?.type || 'linear');
      setYAxisTicksVisible(layout.yaxis?.showticklabels !== false);
      setYAxisMin(layout.yaxis?.range?.[0]?.toString() || '');
      setYAxisMax(layout.yaxis?.range?.[1]?.toString() || '');
      setYAxisInverted(layout.yaxis?.autorange === 'reversed');
      
      // Set legend visibility
      setLegendVisible(layout.showlegend !== false);
      
      // Extract legend items from plot data
      if (plotData.data) {
        const items = plotData.data.map((trace, index) => ({
          id: index,
          name: trace.name || `Trace ${index + 1}`,
          visible: trace.visible !== false && trace.showlegend !== false
        }));
        setLegendItems(items);
      }
      
      // Mark that initial mount is complete
      isInitialMount.current = false;
      
      // Reset expanded states when switching plots
      setTitleExpanded(false);
      setXAxisExpanded(false);
      setYAxisExpanded(false);
      setLegendExpanded(false);
    }
  }, [plotData]);

  // Function to apply updates
  const applyUpdates = () => {
    if (!plotData || !isOpen || isInitialMount.current) return;
    
    
    // Update traces with legend changes
    const updatedData = plotData.data.map((trace, index) => {
      const legendItem = legendItems.find(item => item.id === index);
      if (legendItem) {
        return {
          ...trace,
          name: legendItem.name,
          showlegend: legendVisible && legendItem.visible
        };
      }
      return trace;
    });
    
    const xMinVal = xAxisMin !== '' ? parseFloat(xAxisMin) : null;
    const xMaxVal = xAxisMax !== '' ? parseFloat(xAxisMax) : null;
    
    let xRange = {};
    if (xMinVal !== null && xMaxVal !== null) {
      // Both values set - disable autorange
      xRange = {
        range: [xMinVal, xMaxVal],
        autorange: false
      };
    } else if (xMinVal !== null || xMaxVal !== null) {
      // Only one value set - just set the range without disabling autorange
      xRange = {
        range: [xMinVal, xMaxVal]
      };
    }
    
    
    const updatedLayout = {
      ...plotData.layout,
      title: { 
        ...plotData.layout?.title, 
        text: titleVisible ? titleText : ''
      },
      xaxis: { 
        ...plotData.layout?.xaxis,
        title: { 
          ...plotData.layout?.xaxis?.title,
          text: xAxisLabelVisible ? xAxisLabel : '' 
        },
        type: xAxisScale,
        showticklabels: xAxisTicksVisible,
        ...xRange,
        ...(xAxisInverted && xAxisMin === '' && xAxisMax === '' ? { 
          autorange: 'reversed' 
        } : {})
      },
      yaxis: { 
        ...plotData.layout?.yaxis,
        title: { 
          ...plotData.layout?.yaxis?.title,
          text: yAxisLabelVisible ? yAxisLabel : '' 
        },
        type: yAxisScale,
        showticklabels: yAxisTicksVisible,
        ...(() => {
          const yMinVal = yAxisMin !== '' ? parseFloat(yAxisMin) : null;
          const yMaxVal = yAxisMax !== '' ? parseFloat(yAxisMax) : null;
          
          let yRange = {};
          if (yMinVal !== null && yMaxVal !== null) {
            // Both values set - disable autorange
            yRange = {
              range: [yMinVal, yMaxVal],
              autorange: false
            };
          } else if (yMinVal !== null || yMaxVal !== null) {
            // Only one value set - just set the range without disabling autorange
            yRange = {
              range: [yMinVal, yMaxVal]
            };
          }
          
          if (yAxisInverted && yAxisMin === '' && yAxisMax === '') {
            yRange.autorange = 'reversed';
          }
          
          return yRange;
        })()
      },
      showlegend: legendVisible
    };
    
    
    onUpdate({ ...plotData, data: updatedData, layout: updatedLayout });
  };

  // Apply changes immediately for checkboxes and selects
  useEffect(() => {
    if (!isInitialMount.current) {
      applyUpdates();
    }
  }, [titleVisible, xAxisLabelVisible, yAxisLabelVisible, legendVisible, 
      xAxisScale, yAxisScale, xAxisTicksVisible, yAxisTicksVisible, legendItems,
      xAxisInverted, yAxisInverted]);

  // Apply changes with debounce for text inputs
  useEffect(() => {
    if (!isInitialMount.current) {
      if (updateTimer.current) {
        clearTimeout(updateTimer.current);
      }
      updateTimer.current = setTimeout(() => {
        applyUpdates();
      }, 300);
    }
    
    return () => {
      if (updateTimer.current) {
        clearTimeout(updateTimer.current);
      }
    };
  }, [titleText, xAxisLabel, yAxisLabel, xAxisMin, xAxisMax, yAxisMin, yAxisMax]);

  const updateLegendItem = (id, field, value) => {
    setLegendItems(prev => prev.map(item => 
      item.id === id ? { ...item, [field]: value } : item
    ));
  };

  const handleTextBlur = () => {
    if (updateTimer.current) {
      clearTimeout(updateTimer.current);
    }
    applyUpdates();
  };

  const titleState = {
    expanded: titleExpanded,
    setExpanded: setTitleExpanded,
    visible: titleVisible,
    setVisible: setTitleVisible,
    text: titleText,
    setText: setTitleText
  };

  const xAxisState = {
    expanded: xAxisExpanded,
    setExpanded: setXAxisExpanded,
    labelVisible: xAxisLabelVisible,
    setLabelVisible: setXAxisLabelVisible,
    label: xAxisLabel,
    setLabel: setXAxisLabel,
    scale: xAxisScale,
    setScale: setXAxisScale,
    ticksVisible: xAxisTicksVisible,
    setTicksVisible: setXAxisTicksVisible,
    minValue: xAxisMin,
    setMinValue: setXAxisMin,
    maxValue: xAxisMax,
    setMaxValue: setXAxisMax,
    inverted: xAxisInverted,
    setInverted: setXAxisInverted
  };

  const yAxisState = {
    expanded: yAxisExpanded,
    setExpanded: setYAxisExpanded,
    labelVisible: yAxisLabelVisible,
    setLabelVisible: setYAxisLabelVisible,
    label: yAxisLabel,
    setLabel: setYAxisLabel,
    scale: yAxisScale,
    setScale: setYAxisScale,
    ticksVisible: yAxisTicksVisible,
    setTicksVisible: setYAxisTicksVisible,
    minValue: yAxisMin,
    setMinValue: setYAxisMin,
    maxValue: yAxisMax,
    setMaxValue: setYAxisMax,
    inverted: yAxisInverted,
    setInverted: setYAxisInverted
  };

  const legendState = {
    expanded: legendExpanded,
    setExpanded: setLegendExpanded,
    visible: legendVisible,
    setVisible: setLegendVisible,
    items: legendItems
  };

  return (
    <>
      <div style={{ ...overlayStyle, left: isOpen ? 0 : '-400px' }}>
        <div style={headerStyle}>
          <h3 style={{ margin: 0, fontSize: '1.1rem', color: 'var(--text-color)' }}>Edit Plot</h3>
          <button onClick={onClose} style={closeButtonStyle}>
            ×
          </button>
        </div>
        
        <div style={contentStyle}>
          <AppearanceSection
            appearanceExpanded={appearanceExpanded}
            setAppearanceExpanded={setAppearanceExpanded}
            hasAxes={hasAxes}
            hasLegend={hasLegend}
            titleState={titleState}
            xAxisState={xAxisState}
            yAxisState={yAxisState}
            legendState={legendState}
            onTextBlur={handleTextBlur}
            updateLegendItem={updateLegendItem}
          />

          <DataSection
            dataExpanded={dataExpanded}
            setDataExpanded={setDataExpanded}
          />
        </div>
      </div>
      
      {isOpen && <div style={backdropStyle} onClick={onClose} />}
    </>
  );
};

export default EditPane;