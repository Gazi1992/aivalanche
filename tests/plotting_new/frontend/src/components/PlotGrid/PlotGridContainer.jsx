import React from 'react';
import ColumnSelector from '../ColumnSelector.jsx';
import PlotButton from '../PlotButton.jsx';
import PlotContainer from '../PlotContainer/PlotContainer.jsx';
import { EditIcon, TableIcon, ExpandIcon, DownloadIcon, ResetIcon } from '../icons';
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
  onResetFigure,
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
                <PlotButton
                  onClick={() => onResetFigure(fig)}
                  title="Reset to original"
                  icon={ResetIcon}
                />
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