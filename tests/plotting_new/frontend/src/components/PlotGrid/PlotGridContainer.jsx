import React from 'react';
import Plotly from 'plotly.js-dist-min';
import ColumnSelector from '../ColumnSelector.jsx';
import PlotButton from '../PlotButton.jsx';
import PlotContainer from '../PlotContainer/PlotContainer.jsx';
import { EditIcon, TableIcon, ExpandIcon, DownloadIcon, AutoscaleIcon, LegendToggleIcon } from '../icons';
import { downloadPlotAsImage } from '../../utils/plotUtils';

const PlotGridContainer = ({
  figures,
  gridColumns,
  setGridColumns,
  figureCount,
  nRows,
  gridStyle,
  plotContainerStyle,
  onEditFigure,
  onViewTable,
  onExpandFigure,
  themedLayout
}) => {
  const gridContainerStyle = {
    flex: 1,
    overflowY: nRows > 2 ? 'auto' : 'hidden',
    overflowX: 'hidden',
    padding: 'var(--grid-container-padding)',  // Use CSS variable for padding
    boxSizing: 'border-box',
    display: 'flex',
    flexDirection: 'column'
  };

  const getFigureContainerStyle = (fig) => ({
    ...plotContainerStyle,
    backgroundColor: fig.metadata?.appearance?.background?.figure?.color || 'transparent',
    borderColor: fig.metadata?.appearance?.background?.figure?.borderColor || 'transparent',
    borderWidth: (fig.metadata?.appearance?.background?.figure?.borderColor &&
      fig.metadata?.appearance?.background?.figure?.borderColor !== 'transparent' &&
      fig.metadata?.appearance?.background?.figure?.borderColor !== 'rgba(0,0,0,0)') ? '1px' : '0',
    borderStyle: 'solid'
  });

  const handleEditClick = (fig) => {
    // Don't sync with DOM on edit click - use the figure's stored metadata
    // This avoids cross-contamination issues when multiple plots are present
    onEditFigure(fig);
  };

  const handleDownloadClick = (fig) => {
    downloadPlotAsImage(`plot-${fig.id}`, {
      filename: fig.id || 'plot'
    });
  };

  const handleAutoscaleClick = (fig) => {
    // Autoscale the plot by resetting axis ranges
    const plotDiv = document.getElementById(`plot-${fig.id}`);
    if (plotDiv && plotDiv._fullLayout) {
      const layout = plotDiv._fullLayout;
      const update = {};
      
      // Check if it's a SPLOM by looking for multiple axes
      const isSplom = Object.keys(layout).filter(key => 
        key.startsWith('xaxis') || key.startsWith('yaxis')
      ).length > 2;
      
      if (isSplom) {
        // For SPLOM, autoscale all axes
        Object.keys(layout).forEach(key => {
          if (key.startsWith('xaxis') || key.startsWith('yaxis')) {
            update[`${key}.autorange`] = true;
          }
        });
      } else {
        // Regular plot
        update['xaxis.autorange'] = true;
        update['yaxis.autorange'] = true;
      }
      
      Plotly.relayout(plotDiv, update);
    }
  };

  const handleLegendToggle = (fig) => {
    // Toggle legend visibility
    const plotDiv = document.getElementById(`plot-${fig.id}`);
    if (plotDiv && plotDiv._fullLayout) {
      const currentVisibility = plotDiv._fullLayout.showlegend;
      Plotly.relayout(plotDiv, {
        showlegend: !currentVisibility
      });
    }
  };

  return (
    <>
      <ColumnSelector
        columns={gridColumns}
        onColumnChange={setGridColumns}
        figureCount={figureCount}
      />
      <div className="grid-container" style={gridContainerStyle}>
        <div style={gridStyle}>
          {figures.map(fig => (
            <div 
              key={fig.id} 
              className="plot-container" 
              style={getFigureContainerStyle(fig)}
            >
              <div className="plot-buttons">
                <PlotButton
                  onClick={() => handleEditClick(fig)}
                  title="Edit plot"
                  icon={EditIcon}
                />
                <PlotButton
                  onClick={() => onViewTable(fig)}
                  title="View data"
                  icon={TableIcon}
                />
                <PlotButton
                  onClick={() => handleDownloadClick(fig)}
                  title="Download as PNG"
                  icon={DownloadIcon}
                />
                {/* Show autoscale button only for plots that support zoom/pan */}
                {(fig.metadata?.capabilities?.supportsZoom || fig.metadata?.capabilities?.supportsPan) && (
                  <PlotButton
                    onClick={() => handleAutoscaleClick(fig)}
                    title="Autoscale"
                    icon={AutoscaleIcon}
                  />
                )}
                {/* Show legend toggle only for plots that have legend */}
                {fig.metadata?.capabilities?.hasLegend && (
                  <PlotButton
                    onClick={() => handleLegendToggle(fig)}
                    title="Toggle legend"
                    icon={LegendToggleIcon}
                  />
                )}
                {figures.length > 1 && (
                  <PlotButton
                    onClick={() => onExpandFigure(fig)}
                    title="Expand plot"
                    icon={ExpandIcon}
                  />
                )}
              </div>
              <div style={{ flex: '1 1 auto', minHeight: 0, width: '100%' }}>
                <PlotContainer
                  figure={fig}
                  plotId={`plot-${fig.id}`}
                  themedLayout={themedLayout}
                  onInteraction={(interaction) => {
                    console.log(`Plot ${fig.id} interaction:`, interaction);
                  }}
                />
              </div>
              <div className="figure-id-label">{fig.id}</div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
};

export default PlotGridContainer;