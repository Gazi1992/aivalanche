import React from 'react';
import PlotButton from '../PlotButton';
import PlotContainer from '../PlotContainer/PlotContainer.jsx';
import { EditIcon, TableIcon, DownloadIcon, ResetIcon, ShrinkIcon } from '../icons';
import { downloadPlotAsImage } from '../../utils/plotUtils';
import './ExpandedPlotView.css';

const ExpandedPlotView = ({ activeFig, onClose, onEditFigure, onViewTable, onResetFigure, themedLayout }) => {
  if (!activeFig) return null;

  const handleEditClick = () => {
    // PlotContainer maintains its own state, so we can directly pass the figure
    onEditFigure(activeFig);
  };

  const handleDownloadClick = () => {
    downloadPlotAsImage(`expanded-plot-${activeFig.id}`, {
      filename: activeFig.id || 'plot'
    });
  };

  const handleViewTable = () => {
    onViewTable(activeFig);
  };

  return (
    <div className="expanded-plot-overlay" onClick={onClose}>
      <div className="expanded-plot-container" onClick={e => e.stopPropagation()}>
        <div className="plot-container expanded">
          <div className="plot-buttons">
            <PlotButton
              onClick={handleEditClick}
              title="Edit plot"
              icon={EditIcon}
            />
            <PlotButton
              onClick={handleViewTable}
              title="View data table"
              icon={TableIcon}
            />
            <PlotButton
              onClick={handleDownloadClick}
              title="Download as PNG"
              icon={DownloadIcon}
            />
            <PlotButton
              onClick={() => onResetFigure(activeFig)}
              title="Reset to original"
              icon={ResetIcon}
            />
            <PlotButton
              onClick={onClose}
              title="Shrink plot"
              icon={ShrinkIcon}
            />
          </div>
          <div className="plot-content" style={{ width: '100%', height: 'calc(100% - 40px)' }}>
            <PlotContainer
              figure={activeFig}
              plotId={`expanded-plot-${activeFig.id}`}
              themedLayout={themedLayout}
              onInteraction={(interaction) => {
                console.log(`Expanded plot ${activeFig.id} interaction:`, interaction);
              }}
            />
          </div>
          <div className="figure-id-label">
            {activeFig.id}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExpandedPlotView;