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

// Referencja do elementu HTML <canvas>
const canvasRef = ref(null);
let ctx = null;

// Stan określający, czy użytkownik aktualnie rysuje
const isDrawing = ref(false);

// Przechowywanie ostatnich współrzędnych myszy
let lastX = 0;
let lastY = 0;



// Inicjalizacja tła i parametrów pędzla
const resetCanvasWithWhiteBackground = () => {
  const canvas = canvasRef.value;
  if (!canvas) return;
  
  ctx = canvas.getContext('2d');

  // Fizycznie wypełniamy płótno białym kolorem (rozwiązuje problem przezroczystości)
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Ustawienia pędzla dostosowane do skali MNIST (grubość 35px)
  ctx.strokeStyle = '#000000'; // Czysta czerń
  ctx.lineWidth = 35;           // Gruba linia (odpowiednik ~2px po przeskalowaniu do 28x28)
  ctx.lineCap = 'round';       
  ctx.lineJoin = 'round';      
};

onMounted(() => {
  resetCanvasWithWhiteBackground();
});

// Rozpoczęcie rysowania
const startDrawing = (event) => {
  isDrawing.value = true;
  [lastX, lastY] = [event.offsetX, event.offsetY];
};

// Rysowanie linii podczas ruchu myszy
const draw = (event) => {
  if (!isDrawing.value) return;

  ctx.beginPath();
  ctx.moveTo(lastX, lastY); 
  ctx.lineTo(event.offsetX, event.offsetY); 
  ctx.stroke(); 

  [lastX, lastY] = [event.offsetX, event.offsetY];
};

// Zakończenie rysowania
const stopDrawing = () => {
  isDrawing.value = false;
};

// Czyszczenie całego płótna (i ponowne wypełnienie na biało)
const clearCanvas = () => {
  resetCanvasWithWhiteBackground();
};

const getCanvas = () => {
  return canvasRef.value;
}


// Dla rodzica
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