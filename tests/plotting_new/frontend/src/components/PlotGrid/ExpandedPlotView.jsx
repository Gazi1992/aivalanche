import React from 'react';
import Plotly from 'plotly.js-dist-min';
import PlotButton from '../PlotButton';
import PlotContainer from '../PlotContainer/PlotContainer.jsx';
import { EditIcon, TableIcon, DownloadIcon, AutoscaleIcon, LegendToggleIcon, ShrinkIcon } from '../icons';
import { downloadPlotAsImage } from '../../utils/plotUtils';
import './ExpandedPlotView.css';

const ExpandedPlotView = ({ activeFig, onClose, onEditFigure, onViewTable, themedLayout }) => {
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

  const handleAutoscaleClick = () => {
    // Autoscale the plot by resetting axis ranges
    const plotDiv = document.getElementById(`expanded-plot-${activeFig.id}`);
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

  const handleLegendToggle = () => {
    // Toggle legend visibility
    const plotDiv = document.getElementById(`expanded-plot-${activeFig.id}`);
    if (plotDiv && plotDiv._fullLayout) {
      const currentVisibility = plotDiv._fullLayout.showlegend;
      Plotly.relayout(plotDiv, {
        showlegend: !currentVisibility
      });
    }
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
            {/* Hide autoscale and legend toggle for PCP plots */}
            {activeFig.metadata?.capabilities?.isParallelCoordinates !== true && (
              <>
                <PlotButton
                  onClick={handleAutoscaleClick}
                  title="Autoscale"
                  icon={AutoscaleIcon}
                />
                <PlotButton
                  onClick={handleLegendToggle}
                  title="Toggle legend"
                  icon={LegendToggleIcon}
                />
              </>
            )}
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