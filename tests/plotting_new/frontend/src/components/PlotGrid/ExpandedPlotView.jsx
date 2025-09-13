import React, { useEffect } from 'react';
import PlotButton from '../PlotButton';
import { EditIcon, TableIcon, DownloadIcon, ShrinkIcon } from '../icons';
import { syncFigureWithDOM } from '../../utils/figureManager';
import { downloadPlotAsImage } from '../../utils/plotUtils';
import { renderPlot } from '../../utils/plotRenderer';
import './ExpandedPlotView.css';

const ExpandedPlotView = ({ activeFig, onClose, onEditFigure, onViewTable, themedLayout }) => {
  if (!activeFig) return null;

  useEffect(() => {
    if (activeFig) {
      // Render the plot in expanded view
      const plotId = `expanded-plot-${activeFig.id}`;
      setTimeout(() => {
        renderPlot(activeFig, plotId, themedLayout);
      }, 50);
    }
  }, [activeFig, themedLayout]);

  const handleEditClick = () => {
    const syncedFigure = syncFigureWithDOM(activeFig, `expanded-plot-${activeFig.id}`);
    onEditFigure(syncedFigure);
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
              onClick={onClose}
              title="Shrink plot"
              icon={ShrinkIcon}
            />
          </div>
          <div 
            id={`expanded-plot-${activeFig.id}`} 
            className="plot-content"
            style={{ 
              width: '100%', 
              height: 'calc(100% - 40px)' 
            }} 
          />
          <div className="figure-id-label">
            {activeFig.id}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExpandedPlotView;