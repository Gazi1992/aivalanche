import React from 'react';
import ReferenceDataViewer from '../shared/ReferenceDataViewer';
import { ReferenceData } from '../../types';

interface ReferenceDataTabProps {
  selectedReferenceData: ReferenceData[];
  onAddData: () => void;
  onRemoveData: (dataId: string) => void;
  plotColumns: 1 | 2 | 3;
  selectedDataPages: string[];
  onSelectedDataPagesChange: (pages: string[]) => void;
  expandedDatasets: string[];
  onExpandedDatasetsChange: (datasets: string[]) => void;
}

export const ReferenceDataTab: React.FC<ReferenceDataTabProps> = (props) => {
  return (
    <ReferenceDataViewer
      referenceData={props.selectedReferenceData}
      onAddData={props.onAddData}
      onRemoveData={props.onRemoveData}
      showAddButton={true}
      allowRemove={true}
      plotColumns={props.plotColumns}
      selectedDataPages={props.selectedDataPages}
      onSelectedDataPagesChange={props.onSelectedDataPagesChange}
      expandedDatasets={props.expandedDatasets}
      onExpandedDatasetsChange={props.onExpandedDatasetsChange}
    />
  );
};