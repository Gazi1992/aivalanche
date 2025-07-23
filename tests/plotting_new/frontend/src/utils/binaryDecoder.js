// Decode Plotly's binary data format
export function decodeBinaryData(data) {
  if (!data || typeof data !== 'object') return data;
  
  // Check if this is binary encoded data
  if (data.dtype && data.bdata) {
    const binaryString = atob(data.bdata);
    const bytes = new Uint8Array(binaryString.length);
    
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    
    // Decode based on dtype
    switch (data.dtype) {
      case 'i1': // int8
        return Array.from(new Int8Array(bytes.buffer));
      case 'u1': // uint8
        return Array.from(new Uint8Array(bytes.buffer));
      case 'i2': // int16
        return Array.from(new Int16Array(bytes.buffer));
      case 'u2': // uint16
        return Array.from(new Uint16Array(bytes.buffer));
      case 'i4': // int32
        return Array.from(new Int32Array(bytes.buffer));
      case 'u4': // uint32
        return Array.from(new Uint32Array(bytes.buffer));
      case 'f4': // float32
        return Array.from(new Float32Array(bytes.buffer));
      case 'f8': // float64
        return Array.from(new Float64Array(bytes.buffer));
      default:
        console.warn(`Unknown dtype: ${data.dtype}`);
        return data;
    }
  }
  
  // If not binary data, return as is
  return data;
}