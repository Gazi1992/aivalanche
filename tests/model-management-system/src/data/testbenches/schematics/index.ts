// Import SVG files as URLs
import dcIdVdSvg from './dc_id_vd.svg';
import dcIdVgSvg from './dc_id_vg.svg';
import acSmallSignalSvg from './ac_small_signal.svg';
import transientSwitchingSvg from './transient_switching.svg';
import cvCharacterizationSvg from './cv_characterization.svg';
import noiseAnalysisSvg from './noise_analysis.svg';

// Export as a map for easy access to URLs
export const schematicUrls: Record<string, string> = {
  'schematics/dc_id_vd.svg': dcIdVdSvg,
  'schematics/dc_id_vg.svg': dcIdVgSvg,
  'schematics/ac_small_signal.svg': acSmallSignalSvg,
  'schematics/transient_switching.svg': transientSwitchingSvg,
  'schematics/cv_characterization.svg': cvCharacterizationSvg,
  'schematics/noise_analysis.svg': noiseAnalysisSvg,
};

export default schematicUrls;