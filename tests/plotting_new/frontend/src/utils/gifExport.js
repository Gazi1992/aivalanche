/**
 * GIF Export Utility for Plotly Animations
 *
 * This utility captures frames from a Plotly animation and creates a GIF file.
 * Uses gif.js library for GIF creation.
 */

import GIF from 'gif.js';

/**
 * Export a Plotly animation as a GIF
 * @param {HTMLElement} plotDiv - The Plotly plot div element
 * @param {Object} figure - The figure object with frames
 * @param {Object} options - Export options
 * @returns {Promise} - Resolves with the GIF blob
 */
export async function exportAnimationAsGIF(plotDiv, figure, options = {}) {
  const {
    width = 640,
    height = 480,
    fps = 10,
    quality = 10,
    onProgress = () => {},
    workerScript = '/gif.worker.js'
  } = options;

  // Check if figure has frames
  if (!figure.frames || figure.frames.length === 0) {
    throw new Error('No animation frames found in the figure');
  }

  const frameDelay = 1000 / fps; // Convert FPS to delay in ms
  const frames = figure.frames;

  // Create GIF encoder
  const gif = new GIF({
    workers: 2,
    quality: quality,
    width: width,
    height: height,
    workerScript: workerScript // Worker script location
  });

  // Set up progress handler
  gif.on('progress', onProgress);

  try {
    // Process each frame
    for (let i = 0; i < frames.length; i++) {
      const frame = frames[i];

      // Update plot with frame data
      await updatePlotWithFrame(plotDiv, frame, i);

      // Wait a bit for the plot to render
      await new Promise(resolve => setTimeout(resolve, 100));

      // Capture the frame as an image
      const imageData = await captureFrameAsImage(plotDiv, { width, height });

      // Add frame to GIF
      gif.addFrame(imageData.canvas || imageData, {
        delay: frameDelay,
        copy: true
      });

      // Report progress
      onProgress(i / frames.length);
    }

    // Return promise that resolves with the GIF blob
    return new Promise((resolve, reject) => {
      gif.on('finished', blob => {
        resolve(blob);
      });

      gif.on('error', error => {
        reject(error);
      });

      // Start rendering the GIF
      gif.render();
    });
  } catch (error) {
    console.error('Error creating GIF:', error);
    throw error;
  }
}

/**
 * Update plot with frame data
 * @param {HTMLElement} plotDiv - The Plotly plot div
 * @param {Object} frame - The frame data
 * @param {number} frameIndex - The frame index
 */
async function updatePlotWithFrame(plotDiv, frame, frameIndex) {
  return new Promise((resolve) => {
    // Use Plotly.animate to transition to the frame
    window.Plotly.animate(plotDiv, [frameIndex], {
      frame: {
        duration: 0, // Immediate transition
        redraw: true
      },
      transition: {
        duration: 0
      },
      mode: 'immediate'
    }).then(resolve);
  });
}

/**
 * Capture current plot state as an image
 * @param {HTMLElement} plotDiv - The Plotly plot div
 * @param {Object} options - Capture options
 * @returns {Promise} - Resolves with image data
 */
async function captureFrameAsImage(plotDiv, options = {}) {
  const { width, height } = options;

  return new Promise((resolve, reject) => {
    // Use Plotly's toImage function to get a data URL
    window.Plotly.toImage(plotDiv, {
      format: 'png',
      width: width,
      height: height
    }).then(dataUrl => {
      // Convert data URL to canvas for gif.js
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);
        resolve(canvas);
      };
      img.onerror = reject;
      img.src = dataUrl;
    }).catch(reject);
  });
}

/**
 * Download GIF blob as a file
 * @param {Blob} blob - The GIF blob
 * @param {string} filename - The filename for download
 */
export function downloadGIF(blob, filename = 'animation.gif') {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/**
 * Create a simpler GIF export using Plotly's static export
 * This is a fallback method that doesn't require animation playback
 */
export async function exportStaticFramesAsGIF(plotDiv, figure, options = {}) {
  const {
    width = 640,
    height = 480,
    fps = 10,
    quality = 10,
    onProgress = () => {}
  } = options;

  if (!figure.frames || figure.frames.length === 0) {
    throw new Error('No animation frames found');
  }

  const frameDelay = 1000 / fps;

  // Create a temporary canvas for processing
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');

  // Create GIF encoder with inline worker
  const gif = new GIF({
    workers: 2,
    quality: quality,
    width: width,
    height: height
  });

  gif.on('progress', onProgress);

  // Store original data
  const originalData = [...plotDiv.data];

  try {
    for (let i = 0; i < figure.frames.length; i++) {
      const frame = figure.frames[i];

      // Update plot data with frame data
      if (frame.data) {
        await window.Plotly.react(plotDiv, frame.data, plotDiv.layout);
      }

      // Wait for render
      await new Promise(resolve => setTimeout(resolve, 100));

      // Capture as image
      const dataUrl = await window.Plotly.toImage(plotDiv, {
        format: 'png',
        width: width,
        height: height
      });

      // Load image and add to GIF
      await new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => {
          ctx.clearRect(0, 0, width, height);
          ctx.drawImage(img, 0, 0, width, height);
          gif.addFrame(ctx, {
            delay: frameDelay,
            copy: true
          });
          resolve();
        };
        img.onerror = reject;
        img.src = dataUrl;
      });

      onProgress((i + 1) / figure.frames.length);
    }

    // Restore original data
    await window.Plotly.react(plotDiv, originalData, plotDiv.layout);

    return new Promise((resolve, reject) => {
      gif.on('finished', blob => resolve(blob));
      gif.on('error', error => reject(error));
      gif.render();
    });
  } catch (error) {
    // Restore original data on error
    await window.Plotly.react(plotDiv, originalData, plotDiv.layout);
    throw error;
  }
}