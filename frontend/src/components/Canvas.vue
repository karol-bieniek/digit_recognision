<template>
  <div class="canvas-container">
    <canvas 
      ref="canvasRef" 
      width="500" 
      height="500"
      @mousedown="startDrawing"
      @mousemove="draw"
      @mouseup="stopDrawing"
      @mouseleave="stopDrawing"
    ></canvas>
  </div>
</template>


<script setup>
import { ref, onMounted } from 'vue';

// Reference to the HTML <canvas> element
const canvasRef = ref(null);
let ctx = null;

// State that indicates whether the user is currently drawing
const isDrawing = ref(false);

// Store last mouse coordinates
let lastX = 0;
let lastY = 0;



// Initialize background and brush settings
const resetCanvasWithWhiteBackground = () => {
  const canvas = canvasRef.value;
  if (!canvas) return;
  
  ctx = canvas.getContext('2d');

  // Fill the canvas with white to avoid transparency issues
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Brush settings adjusted for MNIST scale (35px thickness)
  ctx.strokeStyle = '#000000'; // Pure black
  ctx.lineWidth = 35;           // Thick line (~2px after scaling to 28x28)
  ctx.lineCap = 'round';       
  ctx.lineJoin = 'round';      
};

onMounted(() => {
  resetCanvasWithWhiteBackground();
});

// Start drawing
const startDrawing = (event) => {
  isDrawing.value = true;
  [lastX, lastY] = [event.offsetX, event.offsetY];
};

// Draw line while moving the mouse
const draw = (event) => {
  if (!isDrawing.value) return;

  ctx.beginPath();
  ctx.moveTo(lastX, lastY); 
  ctx.lineTo(event.offsetX, event.offsetY); 
  ctx.stroke(); 

  [lastX, lastY] = [event.offsetX, event.offsetY];
};

// Stop drawing
const stopDrawing = () => {
  isDrawing.value = false;
};

// Clear entire canvas (and refill with white)
const clearCanvas = () => {
  resetCanvasWithWhiteBackground();
};

const getCanvas = () => {
  return canvasRef.value;
}


// Expose methods to parent
defineExpose({
  clearCanvas,
  getCanvas,
})

</script>

<style scoped>
.canvas-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0;
  width: 100%;
}

canvas {
  border: 2px solid var(--border-color);
  background-color: var(--bg-white);
  cursor: crosshair;
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  transition: var(--transition);
  display: block;
}

canvas:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow-md);
}

canvas:active {
  cursor: grabbing;
}
</style>