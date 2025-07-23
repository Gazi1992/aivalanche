import { useEffect } from 'react';
import { colorToRgba } from './colorUtils';

export const useEditPaneUpdates = (state, plotData, onUpdate) => {
  const {
    updateTimer,
    isInitialMount,
    titleText,
    xAxisLabel,
    yAxisLabel,
    xAxisMin,
    xAxisMax,
    yAxisMin,
    yAxisMax,
    titleVisible,
    titleAlignment,
    xAxisLabelVisible,
    yAxisLabelVisible,
    xAxisScale,
    yAxisScale,
    xAxisTicksVisible,
    yAxisTicksVisible,
    xAxisInverted,
    yAxisInverted,
    legendVisible,
    legendItems,
    legendBackgroundColor,
    legendBorderColor,
    legendBackgroundOpacity,
    xGridVisible,
    yGridVisible,
    xMinorGridVisible,
    yMinorGridVisible,
    gridOpacity,
    gridColor,
    figureBackgroundColor,
    figureBorderColor,
    plotBackgroundColor,
    plotBorderColor,
    titleFontSize,
    titleBold,
    titleItalic,
    titleColor,
    axisLabelFontSize,
    axisLabelBold,
    axisLabelItalic,
    axisLabelColor,
    axisTickFontSize,
    axisTickColor,
    legendFontSize,
    legendBold,
    legendItalic,
    legendColor
  } = state;

  const applyUpdates = () => {
    if (!plotData || isInitialMount.current) return;

    const updatedLayout = { ...plotData.layout };

    // Update title only if values are not null
    if (titleVisible !== null) {
      updatedLayout.title = {
        ...updatedLayout.title,
        text: titleVisible ? (titleText || '') : '',
        ...(titleAlignment && { xanchor: titleAlignment }),
        ...(titleAlignment && { x: titleAlignment === 'left' ? 0 : titleAlignment === 'right' ? 1 : 0.5 }),
        font: {
          ...updatedLayout.title?.font,
          ...(titleFontSize !== null && { size: titleFontSize }),
          ...(titleColor !== null && { color: titleColor }),
          family: updatedLayout.title?.font?.family || 'Arial, sans-serif'
        }
      };

      // Handle bold/italic for title
      if (titleBold || titleItalic) {
        let fontFamily = updatedLayout.title.font.family || 'Arial, sans-serif';
        if (titleBold && titleItalic) {
          fontFamily = '"Arial Black", Arial, sans-serif';
          updatedLayout.title.font.family = fontFamily;
          updatedLayout.title.font.style = 'italic';
        } else if (titleBold) {
          updatedLayout.title.font.family = '"Arial Black", Arial, sans-serif';
        } else if (titleItalic) {
          updatedLayout.title.font.style = 'italic';
        }
      }
    }

    // Update X-axis only if values are not null
    updatedLayout.xaxis = {
      ...updatedLayout.xaxis,
      title: {
        text: xAxisLabelVisible !== null ? (xAxisLabelVisible ? xAxisLabel : '') : updatedLayout.xaxis?.title?.text || '',
        font: {
          ...updatedLayout.xaxis?.title?.font,
          ...(axisLabelFontSize !== null && { size: axisLabelFontSize }),
          ...(axisLabelColor !== null && { color: axisLabelColor }),
          family: updatedLayout.xaxis?.title?.font?.family || 'Arial, sans-serif'
        }
      },
      ...(xAxisScale !== null && { type: xAxisScale }),
      ...(xAxisTicksVisible !== null && { showticklabels: xAxisTicksVisible }),
      ...(xAxisInverted !== null && { autorange: xAxisInverted ? 'reversed' : (xAxisMin || xAxisMax ? false : true) }),
      ...(xGridVisible !== null && { showgrid: xGridVisible }),
      ...(gridColor !== null && gridOpacity !== null && { gridcolor: colorToRgba(gridColor, gridOpacity) }),
      tickfont: {
        ...updatedLayout.xaxis?.tickfont,
        ...(axisTickFontSize !== null && { size: axisTickFontSize }),
        ...(axisTickColor !== null && { color: axisTickColor })
      },
      showline: true,
      linewidth: 1,
      mirror: true,
      ...(plotBorderColor !== null && { linecolor: plotBorderColor }),
      minor: xMinorGridVisible ? {
        showgrid: true,
        gridcolor: gridColor && gridOpacity ? colorToRgba(gridColor, gridOpacity * 0.5) : 'rgba(128, 128, 128, 0.05)'
      } : {}
    };

    // Handle bold/italic for axis labels
    if ((axisLabelBold || axisLabelItalic) && updatedLayout.xaxis.title.font) {
      let fontFamily = updatedLayout.xaxis.title.font.family || 'Arial, sans-serif';
      if (axisLabelBold && axisLabelItalic) {
        fontFamily = '"Arial Black", Arial, sans-serif';
        updatedLayout.xaxis.title.font.family = fontFamily;
        updatedLayout.xaxis.title.font.style = 'italic';
      } else if (axisLabelBold) {
        updatedLayout.xaxis.title.font.family = '"Arial Black", Arial, sans-serif';
      } else if (axisLabelItalic) {
        updatedLayout.xaxis.title.font.style = 'italic';
      }
    }

    // Set X-axis range if specified
    if (!xAxisInverted && (xAxisMin || xAxisMax)) {
      const currentRange = updatedLayout.xaxis.range || [];
      updatedLayout.xaxis.range = [
        xAxisMin || currentRange[0] || 0,
        xAxisMax || currentRange[1] || 100
      ];
    }

    // Update Y-axis only if values are not null
    updatedLayout.yaxis = {
      ...updatedLayout.yaxis,
      title: {
        text: yAxisLabelVisible !== null ? (yAxisLabelVisible ? yAxisLabel : '') : updatedLayout.yaxis?.title?.text || '',
        font: {
          ...updatedLayout.yaxis?.title?.font,
          ...(axisLabelFontSize !== null && { size: axisLabelFontSize }),
          ...(axisLabelColor !== null && { color: axisLabelColor }),
          family: updatedLayout.yaxis?.title?.font?.family || 'Arial, sans-serif'
        }
      },
      ...(yAxisScale !== null && { type: yAxisScale }),
      ...(yAxisTicksVisible !== null && { showticklabels: yAxisTicksVisible }),
      ...(yAxisInverted !== null && { autorange: yAxisInverted ? 'reversed' : (yAxisMin || yAxisMax ? false : true) }),
      ...(yGridVisible !== null && { showgrid: yGridVisible }),
      ...(gridColor !== null && gridOpacity !== null && { gridcolor: colorToRgba(gridColor, gridOpacity) }),
      tickfont: {
        ...updatedLayout.yaxis?.tickfont,
        ...(axisTickFontSize !== null && { size: axisTickFontSize }),
        ...(axisTickColor !== null && { color: axisTickColor })
      },
      showline: true,
      linewidth: 1,
      mirror: true,
      ...(plotBorderColor !== null && { linecolor: plotBorderColor }),
      minor: yMinorGridVisible ? {
        showgrid: true,
        gridcolor: gridColor && gridOpacity ? colorToRgba(gridColor, gridOpacity * 0.5) : 'rgba(128, 128, 128, 0.05)'
      } : {}
    };

    // Handle bold/italic for Y-axis labels
    if ((axisLabelBold || axisLabelItalic) && updatedLayout.yaxis.title.font) {
      let fontFamily = updatedLayout.yaxis.title.font.family || 'Arial, sans-serif';
      if (axisLabelBold && axisLabelItalic) {
        fontFamily = '"Arial Black", Arial, sans-serif';
        updatedLayout.yaxis.title.font.family = fontFamily;
        updatedLayout.yaxis.title.font.style = 'italic';
      } else if (axisLabelBold) {
        updatedLayout.yaxis.title.font.family = '"Arial Black", Arial, sans-serif';
      } else if (axisLabelItalic) {
        updatedLayout.yaxis.title.font.style = 'italic';
      }
    }

    // Set Y-axis range if specified
    if (!yAxisInverted && (yAxisMin || yAxisMax)) {
      const currentRange = updatedLayout.yaxis.range || [];
      updatedLayout.yaxis.range = [
        yAxisMin || currentRange[0] || 0,
        yAxisMax || currentRange[1] || 100
      ];
    }

    // Update legend only if values are not null
    if (legendVisible !== null) {
      updatedLayout.showlegend = legendVisible;
    }
    
    if (updatedLayout.showlegend !== false) {
      updatedLayout.legend = {
        ...updatedLayout.legend,
        ...(legendBackgroundColor !== null && legendBackgroundOpacity !== null && { 
          bgcolor: colorToRgba(legendBackgroundColor, legendBackgroundOpacity) 
        }),
        ...(legendBorderColor !== null && { 
          bordercolor: legendBorderColor,
          borderwidth: 1 
        }),
        font: {
          ...updatedLayout.legend?.font,
          ...(legendFontSize !== null && { size: legendFontSize }),
          ...(legendColor !== null && { color: legendColor }),
          family: updatedLayout.legend?.font?.family || 'Arial, sans-serif'
        }
      };

      // Handle bold/italic for legend
      if ((legendBold || legendItalic) && updatedLayout.legend.font) {
        let fontFamily = updatedLayout.legend.font.family || 'Arial, sans-serif';
        if (legendBold && legendItalic) {
          fontFamily = '"Arial Black", Arial, sans-serif';
          updatedLayout.legend.font.family = fontFamily;
          updatedLayout.legend.font.style = 'italic';
        } else if (legendBold) {
          updatedLayout.legend.font.family = '"Arial Black", Arial, sans-serif';
        } else if (legendItalic) {
          updatedLayout.legend.font.style = 'italic';
        }
      }
    }

    // Update backgrounds only if values are not null
    if (figureBackgroundColor !== null) {
      updatedLayout.paper_bgcolor = figureBackgroundColor;
      updatedLayout.figureBackgroundColor = figureBackgroundColor;
    }
    if (plotBackgroundColor !== null) {
      updatedLayout.plot_bgcolor = plotBackgroundColor;
    }
    if (figureBorderColor !== null) {
      updatedLayout.figureBorderColor = figureBorderColor;
    }

    // Update traces visibility based on legend items
    const updatedData = plotData.data.map((trace, index) => {
      const legendItem = legendItems.find(item => item.id === index);
      return {
        ...trace,
        showlegend: legendItem ? legendItem.visible : true,
        name: legendItem ? legendItem.name : trace.name
      };
    });

    onUpdate({ ...plotData, layout: updatedLayout, data: updatedData });
  };

  // Handle text blur event
  const handleTextBlur = () => {
    if (updateTimer.current) {
      clearTimeout(updateTimer.current);
    }
    applyUpdates();
  };

  // Apply changes immediately for checkboxes and selects
  useEffect(() => {
    if (!isInitialMount.current) {
      applyUpdates();
    }
  }, [titleVisible, xAxisLabelVisible, yAxisLabelVisible, legendVisible, 
      xAxisScale, yAxisScale, xAxisTicksVisible, yAxisTicksVisible, legendItems,
      xAxisInverted, yAxisInverted, xGridVisible, yGridVisible, 
      xMinorGridVisible, yMinorGridVisible, gridOpacity, gridColor,
      titleFontSize, axisLabelFontSize, axisTickFontSize, titleColor, 
      axisLabelColor, axisTickColor, titleBold, titleItalic, titleAlignment,
      axisLabelBold, axisLabelItalic,
      legendFontSize, legendColor, legendBold, legendItalic,
      legendBackgroundColor, legendBorderColor, legendBackgroundOpacity,
      figureBackgroundColor, figureBorderColor,
      plotBackgroundColor, plotBorderColor]);

  // Auto-update on certain field changes with debounce
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

  return {
    applyUpdates,
    handleTextBlur
  };
};