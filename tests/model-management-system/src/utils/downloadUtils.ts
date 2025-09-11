import JSZip from 'jszip';
import { saveAs } from 'file-saver';
import { Model } from '../types';

// Sample file contents - in a real app, these would be fetched from the server
const getFileContent = (fileName: string, modelName: string): string => {
  // Sample circuit file
  if (fileName.endsWith('.cir')) {
    return `* ${modelName} Circuit File
* Auto-generated model file
* Date: ${new Date().toISOString()}

.subckt ${modelName.toLowerCase().replace(/\s+/g, '_')} d g s b
* Model implementation here
M1 d g s b model_card
.ends

* End of file`;
  }
  
  // Sample lib file
  if (fileName.endsWith('.lib')) {
    return `* Library file for ${modelName}
* Contains model parameters and definitions

.lib ${fileName.replace('.lib', '')}
* Parameter definitions
.param VTH0 = 0.5
.param TOX = 1.4e-9
.endl`;
  }
  
  // Sample CSV parameters
  if (fileName === 'parameters.csv') {
    return `name,subckt,default,min,max,unit,description
VTH0,model,0.5,0.3,0.7,V,Threshold voltage
L,instance,30e-9,28e-9,100e-9,m,Channel length
W,instance,1e-6,100e-9,100e-6,m,Channel width`;
  }
  
  // Sample metadata.json
  if (fileName === 'metadata.json') {
    return JSON.stringify({
      model_id: modelName.replace(/\s+/g, '-'),
      name: modelName,
      version: "1.0.0",
      description: `Model information for ${modelName}`,
      technology: {
        node: "Generic",
        process: "CMOS"
      }
    }, null, 2);
  }
  
  // Sample documentation
  if (fileName.endsWith('.md') || fileName.endsWith('.pdf')) {
    return `# ${modelName} Documentation

## Overview
This is the documentation for the ${modelName} model.

## Usage
Include the model file and instantiate as needed.

## Parameters
See parameters.csv for a complete list of model parameters.

## Support
Contact modeling-support@company.com for assistance.`;
  }
  
  return `Sample content for ${fileName}`;
};

export const downloadModelAsZip = async (model: Model) => {
  const zip = new JSZip();
  const modelFolder = model.model_id;
  
  // Add entry point file
  if (model.files.entry_point) {
    zip.file(
      `${modelFolder}/${model.files.entry_point}`,
      getFileContent(model.files.entry_point, model.name)
    );
  }
  
  // Add parameters file
  if (model.files.parameters_file) {
    zip.file(
      `${modelFolder}/${model.files.parameters_file}`,
      getFileContent(model.files.parameters_file, model.name)
    );
  }
  
  // Add metadata file
  if (model.files.metadata_file) {
    zip.file(
      `${modelFolder}/${model.files.metadata_file}`,
      getFileContent(model.files.metadata_file, model.name)
    );
  }
  
  // Add documentation
  if (model.files.documentation) {
    zip.file(
      `${modelFolder}/${model.files.documentation}`,
      getFileContent(model.files.documentation, model.name)
    );
  }
  
  // Add library files
  if (model.files.lib_directory && model.files.simulation_files) {
    model.files.simulation_files.forEach(file => {
      if (file.endsWith('.lib')) {
        zip.file(
          `${modelFolder}/${model.files.lib_directory}/${file}`,
          getFileContent(file, model.name)
        );
      }
    });
  }
  
  // Generate and download the zip file
  try {
    const content = await zip.generateAsync({ type: 'blob' });
    saveAs(content, `${model.model_id}.zip`);
  } catch (error) {
    console.error('Error creating zip file:', error);
    alert('Failed to create zip file. Please try again.');
  }
};