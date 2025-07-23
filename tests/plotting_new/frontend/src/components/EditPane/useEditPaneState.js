import { useState, useEffect, useRef } from 'react';
import { extractAlphaFromColor, extractColorWithoutAlpha, colorToRgba } from './colorUtils';

export const useEditPaneState = (plotData, isOpen) => {
  // Section expansion states
  const [appearanceExpanded, setAppearanceExpanded] = useState(true);
  const [labelsExpanded, setLabelsExpanded] = useState(false);
  const [axisExpanded, setAxisExpanded] = useState(false);
  const [legendExpanded, setLegendExpanded] = useState(false);
  const [gridExpanded, setGridExpanded] = useState(false);
  const [backgroundExpanded, setBackgroundExpanded] = useState(false);
  const [textExpanded, setTextExpanded] = useState(false);

  // Title state
  const [titleVisible, setTitleVisible] = useState(null);
  const [titleText, setTitleText] = useState(null);
  const [titleAlignment, setTitleAlignment] = useState(null);

  // Axis states
  const [xAxisLabelVisible, setXAxisLabelVisible] = useState(null);
  const [yAxisLabelVisible, setYAxisLabelVisible] = useState(null);
  const [xAxisLabel, setXAxisLabel] = useState(null);
  const [yAxisLabel, setYAxisLabel] = useState(null);
  const [xAxisScale, setXAxisScale] = useState(null);
  const [yAxisScale, setYAxisScale] = useState(null);
  const [xAxisTicksVisible, setXAxisTicksVisible] = useState(null);
  const [yAxisTicksVisible, setYAxisTicksVisible] = useState(null);
  const [xAxisMin, setXAxisMin] = useState('');
  const [xAxisMax, setXAxisMax] = useState('');
  const [yAxisMin, setYAxisMin] = useState('');
  const [yAxisMax, setYAxisMax] = useState('');
  const [xAxisInverted, setXAxisInverted] = useState(null);
  const [yAxisInverted, setYAxisInverted] = useState(null);

  // Legend state
  const [legendVisible, setLegendVisible] = useState(null);
  const [legendItems, setLegendItems] = useState([]);
  const [legendBackgroundColor, setLegendBackgroundColor] = useState(null);
  const [legendBorderColor, setLegendBorderColor] = useState(null);
  const [legendBackgroundOpacity, setLegendBackgroundOpacity] = useState(null);

  // Grid state
  const [xGridVisible, setXGridVisible] = useState(null);
  const [yGridVisible, setYGridVisible] = useState(null);
  const [xMinorGridVisible, setXMinorGridVisible] = useState(false);
  const [yMinorGridVisible, setYMinorGridVisible] = useState(false);
  const [gridOpacity, setGridOpacity] = useState(null);
  const [gridColor, setGridColor] = useState(null);

  // Background state
  const [figureBackgroundColor, setFigureBackgroundColor] = useState(null);
  const [figureBorderColor, setFigureBorderColor] = useState(null);
  const [plotBackgroundColor, setPlotBackgroundColor] = useState(null);
  const [plotBorderColor, setPlotBorderColor] = useState(null);

  // Text styling state
  const [titleFontSize, setTitleFontSize] = useState(null);
  const [titleBold, setTitleBold] = useState(false);
  const [titleItalic, setTitleItalic] = useState(false);
  const [titleColor, setTitleColor] = useState(null);
  const [axisLabelFontSize, setAxisLabelFontSize] = useState(null);
  const [axisLabelBold, setAxisLabelBold] = useState(false);
  const [axisLabelItalic, setAxisLabelItalic] = useState(false);
  const [axisLabelColor, setAxisLabelColor] = useState(null);
  const [axisTickFontSize, setAxisTickFontSize] = useState(null);
  const [axisTickColor, setAxisTickColor] = useState(null);
  const [legendFontSize, setLegendFontSize] = useState(null);
  const [legendBold, setLegendBold] = useState(false);
  const [legendItalic, setLegendItalic] = useState(false);
  const [legendColor, setLegendColor] = useState(null);

  // Timer for updates
  const updateTimer = useRef(null);
  const isInitialMount = useRef(true);

  // Reset subsection states when edit pane is opened
  useEffect(() => {
    if (isOpen) {
      setLabelsExpanded(false);
      setAxisExpanded(false);
      setLegendExpanded(false);
      setGridExpanded(false);
      setTextExpanded(false);
      setBackgroundExpanded(false);
    }
  }, [isOpen]);

  // Initialize state from plotData
  useEffect(() => {
    if (!plotData || !plotData.layout) return;

    const layout = plotData.layout;

    // Title
    setTitleText(layout.title?.text || '');
    setTitleVisible(layout.title?.text ? true : false);
    setTitleAlignment(layout.title?.xanchor || 'center');
    setTitleFontSize(layout.title?.font?.size || 16);
    setTitleColor(layout.title?.font?.color || null);

    // X-axis
    setXAxisLabel(layout.xaxis?.title?.text || '');
    setXAxisLabelVisible(!!layout.xaxis?.title?.text);
    setXAxisScale(layout.xaxis?.type || 'linear');
    setXAxisTicksVisible(layout.xaxis?.showticklabels !== false);
    setXAxisInverted(layout.xaxis?.autorange === 'reversed');
    if (layout.xaxis?.range) {
      setXAxisMin(layout.xaxis.range[0]?.toString() || '');
      setXAxisMax(layout.xaxis.range[1]?.toString() || '');
    }
    setAxisLabelFontSize(layout.xaxis?.title?.font?.size || layout.yaxis?.title?.font?.size || 14);
    setAxisLabelColor(layout.xaxis?.title?.font?.color || layout.yaxis?.title?.font?.color || null);
    setAxisTickFontSize(layout.xaxis?.tickfont?.size || layout.yaxis?.tickfont?.size || 12);
    setAxisTickColor(layout.xaxis?.tickfont?.color || layout.yaxis?.tickfont?.color || null);
    setXGridVisible(layout.xaxis?.showgrid !== false);
    if (layout.xaxis?.gridcolor) {
      setGridColor(extractColorWithoutAlpha(layout.xaxis.gridcolor));
      setGridOpacity(extractAlphaFromColor(layout.xaxis.gridcolor));
    }
    setXMinorGridVisible(layout.xaxis?.minor?.showgrid === true);

    // Y-axis
    setYAxisLabel(layout.yaxis?.title?.text || '');
    setYAxisLabelVisible(!!layout.yaxis?.title?.text);
    setYAxisScale(layout.yaxis?.type || 'linear');
    setYAxisTicksVisible(layout.yaxis?.showticklabels !== false);
    setYAxisInverted(layout.yaxis?.autorange === 'reversed');
    if (layout.yaxis?.range) {
      setYAxisMin(layout.yaxis.range[0]?.toString() || '');
      setYAxisMax(layout.yaxis.range[1]?.toString() || '');
    }
    setYGridVisible(layout.yaxis?.showgrid !== false);
    setYMinorGridVisible(layout.yaxis?.minor?.showgrid === true);

    // Legend
    setLegendVisible(layout.showlegend !== false);
    if (layout.legend?.bgcolor) {
      setLegendBackgroundColor(extractColorWithoutAlpha(layout.legend.bgcolor));
      setLegendBackgroundOpacity(extractAlphaFromColor(layout.legend.bgcolor));
    } else {
      // Only set defaults if not specified in layout
      setLegendBackgroundColor(null);
      setLegendBackgroundOpacity(0.8);
    }
    setLegendBorderColor(layout.legend?.bordercolor || null);
    setLegendFontSize(layout.legend?.font?.size || 12);
    setLegendColor(layout.legend?.font?.color || null);

    // Legend items from traces
    if (plotData.data) {
      const items = plotData.data.map((trace, index) => ({
        id: index,
        name: trace.name || `Trace ${index + 1}`,
        visible: trace.visible !== false
      }));
      setLegendItems(items);
    }

    // Backgrounds
    setFigureBackgroundColor(layout.figureBackgroundColor || layout.paper_bgcolor || null);
    setFigureBorderColor(layout.figureBorderColor || null);
    setPlotBackgroundColor(layout.plot_bgcolor || null);
    // Extract plot border color from axis line color if present
    setPlotBorderColor(layout.xaxis?.linecolor || layout.yaxis?.linecolor || null);

    // Mark initial mount as done
    setTimeout(() => {
      isInitialMount.current = false;
    }, 100);
  }, [plotData]);

  return {
    // Section expansion states
    appearanceExpanded,
    setAppearanceExpanded,
    labelsExpanded,
    setLabelsExpanded,
    axisExpanded,
    setAxisExpanded,
    legendExpanded,
    setLegendExpanded,
    gridExpanded,
    setGridExpanded,
    backgroundExpanded,
    setBackgroundExpanded,
    textExpanded,
    setTextExpanded,

    // Title state
    titleVisible,
    setTitleVisible,
    titleText,
    setTitleText,
    titleAlignment,
    setTitleAlignment,

    // Axis states
    xAxisLabelVisible,
    setXAxisLabelVisible,
    yAxisLabelVisible,
    setYAxisLabelVisible,
    xAxisLabel,
    setXAxisLabel,
    yAxisLabel,
    setYAxisLabel,
    xAxisScale,
    setXAxisScale,
    yAxisScale,
    setYAxisScale,
    xAxisTicksVisible,
    setXAxisTicksVisible,
    yAxisTicksVisible,
    setYAxisTicksVisible,
    xAxisMin,
    setXAxisMin,
    xAxisMax,
    setXAxisMax,
    yAxisMin,
    setYAxisMin,
    yAxisMax,
    setYAxisMax,
    xAxisInverted,
    setXAxisInverted,
    yAxisInverted,
    setYAxisInverted,

    // Legend state
    legendVisible,
    setLegendVisible,
    legendItems,
    setLegendItems,
    legendBackgroundColor,
    setLegendBackgroundColor,
    legendBorderColor,
    setLegendBorderColor,
    legendBackgroundOpacity,
    setLegendBackgroundOpacity,

    // Grid state
    xGridVisible,
    setXGridVisible,
    yGridVisible,
    setYGridVisible,
    xMinorGridVisible,
    setXMinorGridVisible,
    yMinorGridVisible,
    setYMinorGridVisible,
    gridOpacity,
    setGridOpacity,
    gridColor,
    setGridColor,

    // Background state
    figureBackgroundColor,
    setFigureBackgroundColor,
    figureBorderColor,
    setFigureBorderColor,
    plotBackgroundColor,
    setPlotBackgroundColor,
    plotBorderColor,
    setPlotBorderColor,

    // Text styling state
    titleFontSize,
    setTitleFontSize,
    titleBold,
    setTitleBold,
    titleItalic,
    setTitleItalic,
    titleColor,
    setTitleColor,
    axisLabelFontSize,
    setAxisLabelFontSize,
    axisLabelBold,
    setAxisLabelBold,
    axisLabelItalic,
    setAxisLabelItalic,
    axisLabelColor,
    setAxisLabelColor,
    axisTickFontSize,
    setAxisTickFontSize,
    axisTickColor,
    setAxisTickColor,
    legendFontSize,
    setLegendFontSize,
    legendBold,
    setLegendBold,
    legendItalic,
    setLegendItalic,
    legendColor,
    setLegendColor,

    // Refs
    updateTimer,
    isInitialMount
  };
};