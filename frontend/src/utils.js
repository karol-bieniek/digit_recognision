export const getCanvasBlob = (canvas, format = 'image/png') => {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) {
        resolve(blob);
      } else {
        reject(new Error('Płótno jest puste!'));
      }
    }, format);
  });
};