import React from 'react';
import ModelReport from '../ModelReport';
import { Model, ReferenceData, ModelParameter } from '../../types';

interface DocumentationTabProps {
  selectedModelTemplate?: Model;
  selectedReferenceData: ReferenceData[];
  parameters: (ModelParameter & { optimize: boolean; value?: number })[];
  displayedCalibrationResults: any;
  documentationData: any;
  documentationGenerated: boolean;
  isGeneratingReport: boolean;
  reportGenerationProgress: number;
  onGenerateDocumentation: () => void;
  onReleaseModel?: () => void;
  isReleased?: boolean;
}

export const DocumentationTab: React.FC<DocumentationTabProps> = ({
  selectedModelTemplate,
  selectedReferenceData,
  parameters,
  displayedCalibrationResults,
  documentationData,
  documentationGenerated,
  isGeneratingReport,
  reportGenerationProgress,
  onGenerateDocumentation,
  onReleaseModel,
  isReleased = false
}) => {
  return (
    <div className="h-full overflow-y-auto p-4">
      <ModelReport
        modelData={documentationData?.model || selectedModelTemplate}
        referenceData={documentationData?.refData || selectedReferenceData}
        parameters={documentationData?.params || parameters}
        calibrationResults={documentationData?.calibrationResults || displayedCalibrationResults}
        timestamp={documentationData?.timestamp}
        onGenerateReport={onGenerateDocumentation}
        isGenerated={documentationGenerated}
        showGenerateButton={true}
        isGenerating={isGeneratingReport}
        generationProgress={reportGenerationProgress}
        onReleaseModel={onReleaseModel}
        isReleased={isReleased}
      />
    </div>
  );
};