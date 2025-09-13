import React from 'react';
import ColumnSelector from '../ColumnSelector.jsx';
import PlotButton from '../PlotButton.jsx';
import { EditIcon, TableIcon, ExpandIcon, DownloadIcon } from '../icons';
import { syncFigureWithDOM } from '../../utils/figureManager';
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
  onExpandFigure
}) => {
  const gridContainerStyle = {
    flex: 1,
    overflowY: nRows > 2 ? 'auto' : 'hidden',
    overflowX: 'hidden',
    padding: figureCount === 1 ? '20px' : '0 20px 20px 20px',
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
    // With single plot, syncFigureWithDOM should work correctly
    const syncedFigure = syncFigureWithDOM(fig, `plot-${fig.id}`);
    onEditFigure(syncedFigure);
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
                {figures.length > 1 && (
                  <PlotButton
                    onClick={() => onExpandFigure(fig)}
                    title="Expand plot"
                    icon={ExpandIcon}
                  />
                )}
                <PlotButton
                  onClick={() => handleDownloadClick(fig)}
                  title="Download as PNG"
                  icon={DownloadIcon}
                />
              </div>
              <div 
                id={`plot-${fig.id}`} 
                style={{ flex: '1 1 auto', minHeight: 0, width: '100%' }}
              />
              <div className="figure-id-label">{fig.id}</div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
};

export default PlotGridContainer;