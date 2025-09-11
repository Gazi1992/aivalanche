import React from 'react';
import ReferenceDataViewer from '../shared/ReferenceDataViewer';
import { ReferenceData, ModelParameter } from '../../types';

interface SimulationsTabProps {
  selectedReferenceData: ReferenceData[];
  simulationResults: any;
  onRunSimulation: () => void;
  isSimulating: boolean;
  simulationProgress: number;
  parameters: (ModelParameter & { optimize: boolean; value?: number })[];
  onParameterChange: (index: number, field: string, value: any) => void;
  plotColumns: 1 | 2 | 3;
  selectedDataPages: string[];
  onSelectedDataPagesChange: (pages: string[]) => void;
  expandedDatasets: string[];
  onExpandedDatasetsChange: (datasets: string[]) => void;
}

export const SimulationsTab: React.FC<SimulationsTabProps> = (props) => {
  return (
    <ReferenceDataViewer
      referenceData={props.selectedReferenceData}
      simulationData={props.simulationResults}
      onRunSimulation={props.onRunSimulation}
      isSimulating={props.isSimulating}
      simulationProgress={props.simulationProgress}
      showParametersPanel={true}
      parameters={props.parameters}
      onParameterChange={props.onParameterChange}
      showAddButton={false}
      allowRemove={false}
      plotColumns={props.plotColumns}
      compactDataView={true}
      selectedDataPages={props.selectedDataPages}
      onSelectedDataPagesChange={props.onSelectedDataPagesChange}
      expandedDatasets={props.expandedDatasets}
      onExpandedDatasetsChange={props.onExpandedDatasetsChange}
    />
  );
};