import React from 'react';
import PlotContainer from '../PlotContainer/PlotContainer.jsx';
import './ExpandedPlotView.css';

const ExpandedPlotView = ({ activeFig, onClose, onEditFigure, onViewTable, themedLayout }) => {
  if (!activeFig) return null;

  return (
    <div className="expanded-plot-overlay" onClick={onClose}>
      <div className="expanded-plot-container" onClick={e => e.stopPropagation()}>
        <div className="plot-container expanded">
          <PlotContainer
            figure={activeFig}
            plotId={`expanded-plot-${activeFig.id}`}
            themedLayout={themedLayout}
            onEdit={() => onEditFigure(activeFig)}
            onViewTable={() => onViewTable(activeFig)}
            onExpand={onClose}
            isExpanded={true}
            showExpandButton={true}
            onInteraction={(interaction) => {
              console.log(`Expanded plot ${activeFig.id} interaction:`, interaction);
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default ExpandedPlotView;