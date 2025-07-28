import { useEffect } from 'react';

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
    xGridVisible,
    yGridVisible,
    xMinorGridVisible,
    yMinorGridVisible,
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
    legendTextColor,
    traceProperties
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
          ...(titleColor !== null && { color: titleColor })
        }
      };

      // Handle bold/italic for title
      if (titleBold && updatedLayout.title.font) {
        updatedLayout.title.font.weight = 'bold';
      }
      if (titleItalic && updatedLayout.title.font) {
        updatedLayout.title.font.style = 'italic';
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
          ...(axisLabelColor !== null && { color: axisLabelColor })
        }
      },
      ...(xAxisScale !== null && { type: xAxisScale }),
      ...(xAxisTicksVisible !== null && { showticklabels: xAxisTicksVisible }),
      ...(xAxisInverted !== null && { autorange: xAxisInverted ? 'reversed' : (xAxisMin || xAxisMax ? false : true) }),
      ...(xGridVisible !== null && { showgrid: xGridVisible }),
      ...(gridColor !== null && { gridcolor: gridColor }),
      ...(gridColor !== null && { zerolinecolor: gridColor }),
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
        gridcolor: gridColor || 'rgba(128, 128, 128, 0.1)'
      } : {}
    };

    // Handle bold/italic for axis labels
    if (axisLabelBold && updatedLayout.xaxis.title.font) {
      updatedLayout.xaxis.title.font.weight = 'bold';
    }
    if (axisLabelItalic && updatedLayout.xaxis.title.font) {
      updatedLayout.xaxis.title.font.style = 'italic';
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
          ...(axisLabelColor !== null && { color: axisLabelColor })
        }
      },
      ...(yAxisScale !== null && { type: yAxisScale }),
      ...(yAxisTicksVisible !== null && { showticklabels: yAxisTicksVisible }),
      ...(yAxisInverted !== null && { autorange: yAxisInverted ? 'reversed' : (yAxisMin || yAxisMax ? false : true) }),
      ...(yGridVisible !== null && { showgrid: yGridVisible }),
      ...(gridColor !== null && { gridcolor: gridColor }),
      ...(gridColor !== null && { zerolinecolor: gridColor }),
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
        gridcolor: gridColor || 'rgba(128, 128, 128, 0.1)'
      } : {}
    };

    // Handle bold/italic for Y-axis labels
    if (axisLabelBold && updatedLayout.yaxis.title.font) {
      updatedLayout.yaxis.title.font.weight = 'bold';
    }
    if (axisLabelItalic && updatedLayout.yaxis.title.font) {
      updatedLayout.yaxis.title.font.style = 'italic';
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
        ...(legendBackgroundColor !== null && { 
          bgcolor: legendBackgroundColor 
        }),
        ...(legendBorderColor !== null && { 
          bordercolor: legendBorderColor,
          borderwidth: 1 
        }),
        font: {
          ...updatedLayout.legend?.font,
          ...(legendFontSize !== null && { size: legendFontSize }),
          ...(legendTextColor !== null && { color: legendTextColor })
        }
      };

      // Handle bold/italic for legend
      if (legendBold && updatedLayout.legend.font) {
        updatedLayout.legend.font.weight = 'bold';
      }
      if (legendItalic && updatedLayout.legend.font) {
        updatedLayout.legend.font.style = 'italic';
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

    // Update traces visibility based on legend items and trace properties
    const updatedData = plotData.data.map((trace, index) => {
      const legendItem = legendItems.find(item => item.id === index);
      const traceProps = traceProperties[index] || {};
      
      const updatedTrace = {
        ...trace,
        showlegend: legendItem ? legendItem.visible : true,
        name: traceProps.name !== undefined ? traceProps.name : (legendItem ? legendItem.name : trace.name)
      };
      
      // Update line properties if it's a line trace
      if (trace.mode?.includes('lines')) {
        updatedTrace.line = {
          ...trace.line,
          ...(traceProps.lineWidth !== undefined && { width: traceProps.lineWidth }),
          ...(traceProps.lineStyle !== undefined && { dash: traceProps.lineStyle }),
          ...(traceProps.color !== undefined && !traceProps.colorColumn && { color: traceProps.color })
        };
        
        // Handle symbols for line traces
        if (traceProps.symbol !== undefined || traceProps.symbolSize !== undefined) {
          const currentSymbol = traceProps.symbol !== undefined ? traceProps.symbol : trace.marker?.symbol;
          const currentSize = traceProps.symbolSize !== undefined ? traceProps.symbolSize : trace.marker?.size;
          
          // Set mode based on symbol and size
          if (currentSymbol === null || currentSize === 0) {
            updatedTrace.mode = 'lines';
          } else {
            updatedTrace.mode = 'lines+markers';
            
            // Update marker properties
            updatedTrace.marker = {
              ...trace.marker,
              ...(traceProps.symbol !== undefined && { symbol: traceProps.symbol }),
              ...(traceProps.symbolSize !== undefined && { size: traceProps.symbolSize }),
              ...(traceProps.symbolColor !== undefined && { color: traceProps.symbolColor })
            };
            
            // Only set line properties if border color is explicitly set
            if (traceProps.symbolBorderColor !== undefined) {
              updatedTrace.marker.line = {
                ...trace.marker?.line,
                color: traceProps.symbolBorderColor,
                width: 1
              };
            }
          }
        }
      }
      
      // Update marker properties if it's a scatter trace
      if (trace.mode?.includes('markers') && !trace.mode?.includes('lines')) {
        // Check if we should hide markers
        const currentSymbol = traceProps.symbol !== undefined ? traceProps.symbol : trace.marker?.symbol;
        const currentSize = traceProps.symbolSize !== undefined ? traceProps.symbolSize : trace.marker?.size;
        
        if (currentSymbol === null || currentSize === 0) {
          // Hide scatter plot if no symbol
          updatedTrace.visible = false;
        } else {
          updatedTrace.visible = legendItem ? legendItem.visible : true;
          
          updatedTrace.marker = {
            ...trace.marker,
            ...(traceProps.symbol !== undefined && { symbol: traceProps.symbol }),
            ...(traceProps.symbolSize !== undefined && { size: traceProps.symbolSize }),
            ...(traceProps.symbolColor !== undefined && { color: traceProps.symbolColor }),
            ...(traceProps.color !== undefined && !traceProps.colorColumn && !traceProps.symbolColor && { color: traceProps.color })
          };
          
          // Only set line properties if border color is explicitly set
          if (traceProps.symbolBorderColor !== undefined) {
            updatedTrace.marker.line = {
              ...trace.marker?.line,
              color: traceProps.symbolBorderColor,
              width: 1
            };
          }
          
          // Handle color by column
          if (traceProps.colorColumn && plotData.x && plotData.y) {
            // This would need access to the actual data columns
            // For now, we'll just set up the structure
            updatedTrace.marker.color = traceProps.colorColumn; // This should be the actual data
            updatedTrace.marker.colorscale = traceProps.colormap || 'Viridis';
            updatedTrace.marker.showscale = traceProps.showColorbar !== false;
            if (traceProps.showColorbar !== false) {
              updatedTrace.marker.colorbar = {
                title: {
                  text: traceProps.colorbarTitle || traceProps.colorColumn,
                  font: { weight: 'normal' }
                },
                tickfont: { weight: 'normal' },
                ...(traceProps.showColorbarTicks === false && { tickmode: 'array', tickvals: [] })
              };
            }
          }
        }
      }
      
      // Update bar properties if it's a bar trace
      if (trace.type === 'bar') {
        // Bar width
        if (traceProps.barWidth !== undefined) {
          updatedTrace.width = traceProps.barWidth;
        }
        
        // Bar opacity
        if (traceProps.barOpacity !== undefined) {
          updatedTrace.opacity = traceProps.barOpacity;
        }
        
        // Bar color
        if (traceProps.color !== undefined && !traceProps.colorColumn) {
          updatedTrace.marker = {
            ...updatedTrace.marker,
            color: traceProps.color
          };
        }
        
        // Text on bars
        if (traceProps.showText !== undefined) {
          if (traceProps.showText) {
            // Show the y values as text on bars
            updatedTrace.text = trace.y;
            updatedTrace.textposition = traceProps.textPosition || 'auto';
          } else {
            updatedTrace.text = undefined;
            updatedTrace.textposition = undefined;
          }
        } else if (traceProps.textPosition !== undefined && trace.text) {
          updatedTrace.textposition = traceProps.textPosition;
        }
        
        // Handle color by column for bars
        if (traceProps.colorColumn && plotData.x && plotData.y) {
          updatedTrace.marker = {
            ...updatedTrace.marker,
            color: traceProps.colorColumn, // This should be the actual data
            colorscale: traceProps.colormap || 'Viridis',
            showscale: traceProps.showColorbar !== false
          };
          if (traceProps.showColorbar !== false) {
            updatedTrace.marker.colorbar = {
              title: {
                text: traceProps.colorbarTitle || traceProps.colorColumn,
                font: { weight: 'normal' }
              },
              tickfont: { weight: 'normal' },
              ...(traceProps.showColorbarTicks === false && { tickmode: 'array', tickvals: [] })
            };
          }
        }
      }
      
      return updatedTrace;
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
      xMinorGridVisible, yMinorGridVisible, gridColor,
      titleFontSize, axisLabelFontSize, axisTickFontSize, titleColor, 
      axisLabelColor, axisTickColor, titleBold, titleItalic, titleAlignment,
      axisLabelBold, axisLabelItalic,
      legendFontSize, legendTextColor, legendBold, legendItalic,
      legendBackgroundColor, legendBorderColor,
      figureBackgroundColor, figureBorderColor,
      plotBackgroundColor, plotBorderColor, traceProperties]);

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