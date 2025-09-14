import React from 'react';
import ColumnSelector from '../ColumnSelector.jsx';
import PlotContainer from '../PlotContainer/PlotContainer.jsx';

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
              <PlotContainer
                figure={fig}
                plotId={`plot-${fig.id}`}
                themedLayout={themedLayout}
                onEdit={() => onEditFigure(fig)}
                onViewTable={() => onViewTable(fig)}
                onExpand={() => onExpandFigure(fig)}
                isExpanded={false}
                showExpandButton={figures.length > 1}
                onInteraction={(interaction) => {
                  console.log(`Plot ${fig.id} interaction:`, interaction);
                }}
              />
            </div>
          ))}
        </div>
      </div>
    </>
  );
};

export default PlotGridContainer;