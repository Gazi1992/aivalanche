import React from 'react';
import PlotContainer from '../PlotContainer/PlotContainer.jsx';
import D3Container from '../D3Container/D3Container.jsx';
import './ExpandedPlotView.css';

const ExpandedPlotView = ({ activeFig, onClose, onEditFigure, onViewTable, themedLayout }) => {
  if (!activeFig) return null;

  return (
    <div className="expanded-plot-overlay" onClick={onClose}>
      <div className="expanded-plot-container" onClick={e => e.stopPropagation()}>
        <div className="plot-container expanded">
          {activeFig.type === 'd3' ? (
            <D3Container
              figure={activeFig}
              vizId={`expanded-d3-${activeFig.id}`}
              onEdit={activeFig.metadata?.isEditable !== false ? (() => onEditFigure(activeFig)) : null}
              onViewTable={() => onViewTable(activeFig)}
              onExpand={onClose}
              isExpanded={true}
              showExpandButton={true}
              onInteraction={(interaction) => {
                console.log(`Expanded D3 ${activeFig.id} interaction:`, interaction);
              }}
            />
          ) : (
            <PlotContainer
              figure={activeFig}
              plotId={`expanded-plot-${activeFig.id}`}
              themedLayout={themedLayout}
              onEdit={activeFig.metadata?.isEditable !== false ? (() => onEditFigure(activeFig)) : null}
              onViewTable={() => onViewTable(activeFig)}
              onExpand={onClose}
              isExpanded={true}
              showExpandButton={true}
              onInteraction={(interaction) => {
                console.log(`Expanded plot ${activeFig.id} interaction:`, interaction);
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default ExpandedPlotView;