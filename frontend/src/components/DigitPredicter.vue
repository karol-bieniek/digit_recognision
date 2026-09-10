<script setup>

import { ref, onMounted } from 'vue';
import { sendImgDigit, saveCanvas, retrain } from '../../api/predict.ts';
import Canvas from './Canvas.vue';
import { getCanvasBlob } from '../utils';



// Model predictions
const prediction = ref(null);
const confidence = ref(null);

const canvasActions = ref(null);


const isReview = ref(false);
const isSuccess = ref(false);
const correctNumber = ref(null);

const isRetraining = ref(false);

const clearCanvas = () => {
    canvasActions.value.clearCanvas();
}


// Send drawing to backend
const uploadImage = async () => {
  const canvas = canvasActions.value.getCanvas();
  try {
      const imageBlob = await getCanvasBlob(canvas);
      const formData = new FormData();
      formData.append('drawing', imageBlob, 'user-drawing.png');

      const response = await sendImgDigit(formData);
      if (response !== null) {
        prediction.value = response.prediction;
        confidence.value = response.confidence;
      } else {
        alert('Upload failed (server returned an error).');
      }

  } catch (error) {
    console.error('Network error:', error);
  }
};


const handleYes = async () => {
  const canvas = canvasActions.value.getCanvas();
  const imageBlob = await getCanvasBlob(canvas);

  const formData = new FormData();
  formData.append('drawing', imageBlob, 'user-drawing.png');
  formData.append('prediction', prediction.value);
  formData.append('confidence', confidence.value);
  const correctDigit = prediction.value; // If the user confirms, the correct digit is the one predicted by the model
  formData.append('correct_digit', correctDigit);
  

  try {
      const response = await saveCanvas(formData);
      if (response === null) {
          alert("Server error");
      } else {
        console.log("Prediction saved in the database");
      }
  } catch (error) {
      console.error('Network error:', error);
  }

  isReview.value = false;
  isSuccess.value = true;
}


const handleNo = () => {
  isReview.value = true;
  isSuccess.value = false;
}


const handleReview = async () => {

  if (!prediction.value || !confidence.value) {
    alert("No prediction has been made yet!");
    return;
  }


  const canvas = canvasActions.value.getCanvas();
  try {
    const imageBlob = await getCanvasBlob(canvas);
    const formData = new FormData();
    formData.append('drawing', imageBlob, 'drawing.png');
    formData.append('prediction', prediction.value);
    formData.append('confidence', confidence.value);
    formData.append('correct_digit', correctNumber.value);

    const response = await saveCanvas(formData);
    if (response === null) {
      alert("Server error");
    } else {
      isReview.value = false;
      isSuccess.value = true;
    }
  } catch (error) {
    console.error('Network error:', error);
  }
}


const handleRetrain = async () => {
  isRetraining.value = true; 
  try {
    await retrain();
  } catch (error) {
    console.log("Training error: ", error);
  } finally {
    isRetraining.value = false; 
  }
}

</script>

<template>
  <div class="main-wrapper">
    <!-- Canvas and drawing section -->
    <div class="canvas-section">
      <h2 class="section-title">Digit Recognition</h2>
      <p class="subtitle">Draw a digit with your mouse on the canvas below</p>
      
      <Canvas ref="canvasActions" class="canvas-element"/>

      <!-- Canvas control buttons -->
      <div class="controls">
        <button @click="clearCanvas" class="btn btn-clear">
          <span class="btn-icon">✕</span> Clear
        </button>
        <button @click="uploadImage" class="btn btn-save">
          <span class="btn-icon">✓</span> Analyze
        </button>
      </div>

      <!-- Prediction results -->
      <div class="prediction-section" v-if="prediction !== null">
        <div class="prediction-box">
          <div class="prediction-result">
            <span class="result-label">Recognized digit:</span>
            <span class="result-value">{{ prediction }}</span>
          </div>
          <div class="confidence-bar">
            <span class="confidence-label">Prediction confidence:</span>
            <div class="confidence-container">
              <div class="confidence-fill" :style="{ width: confidence + '%' }"></div>
              <span class="confidence-text">{{ confidence }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Prediction review modal -->
    <div class="modal-overlay" v-if="prediction !== null">
      <div class="modal-content">

        <h3 class="modal-title" v-if="!isReview && !isSuccess">Was the digit recognized correctly?</h3>
        <!-- Yes/No buttons -->
        <div class="modal-actions" v-if="!isReview && !isSuccess">

          <button type="button" @click="handleYes" class="btn btn-success">Yes, it's correct</button>
          <button type="button" @click="handleNo" class="btn btn-warning">No, correct it</button>
        </div>

        <!-- Correction form -->
        <form @submit.prevent="handleReview" v-if="isReview" class="correction-form">
          <div class="form-group">
            <label for="correct-number">Which digit should have been recognized?</label>
            <input 
              id="correct-number" 
              v-model.number="correctNumber" 
              type="number" 
              min="0"
              max="9"
              placeholder="Enter a digit (0-9)"
              class="form-input"
            />
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary">Submit correction</button>
            <button type="button" @click="isReview = false" class="btn btn-secondary">Cancel</button>
          </div>
        </form>

        <!-- Success confirmation -->
        <div class="success-message" v-if="isSuccess">
          <p class="success-text">✓ Thanks for your feedback!</p>
          <p class="success-subtitle">Your input helps improve model training</p>
          <div class="success-actions">
            <button type="button" @click="isSuccess = false; prediction = null" class="btn btn-primary">Close</button>
          </div>
        </div>
      </div>
    </div>
      <div>
        <button 
          type="button" 
          @click="handleRetrain" 
          class="btn btn-retrain"
          :disabled="isRetraining"
        >
          <span v-if="!isRetraining">Retrain model</span>
          <span v-else>Training...</span>
        </button>
      </div>
  </div>
</template>


<style scoped>
/* ==================== MAIN CONTAINER ==================== */
.main-wrapper {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  background-color: var(--bg-light);
  min-height: 100vh;
}

/* ==================== CANVAS SECTION ==================== */
.canvas-section {
  background-color: var(--bg-white);
  border-radius: var(--radius);
  padding: 2rem;
  box-shadow: var(--shadow-md);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section-title {
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--text-dark);
  margin: 0;
  padding-bottom: 0.5rem;
  border-bottom: 3px solid var(--primary-color);
}

.subtitle {
  color: var(--text-muted);
  font-size: 0.95rem;
  margin: 0;
  font-weight: 500;
}

/* ==================== CANVAS ELEMENT ==================== */
.canvas-element {
  border: 2px solid var(--border-color);
  border-radius: var(--radius);
  background-color: #fafafa;
  transition: var(--transition);
  box-shadow: var(--shadow-sm);
}

.canvas-element:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow-md);
}

/* ==================== BUTTONS ==================== */
.controls {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: flex-start;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: var(--radius);
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: var(--shadow-sm);
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.btn:active {
  transform: translateY(0);
  box-shadow: var(--shadow-sm);
}

.btn-icon {
  font-size: 1.1rem;
  font-weight: bold;
}

.btn-clear {
  background-color: var(--danger-color);
  color: white;
}

.btn-clear:hover {
  background-color: #dc2626;
}

.btn-save {
  background-color: var(--success-color);
  color: white;
  flex: 1;
  min-width: 200px;
}

.btn-save:hover {
  background-color: #059669;
}

/* ==================== PREDICTION SECTION ==================== */
.prediction-section {
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.prediction-box {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: var(--radius);
  padding: 1.5rem;
  color: white;
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 1.5rem;
  box-shadow: var(--shadow-md);
}

/* Prediction result */
.prediction-result {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 1rem;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius);
}

.result-label {
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  opacity: 0.9;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.result-value {
  font-size: 3rem;
  font-weight: 800;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

/* Confidence bar */
.confidence-bar {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.confidence-label {
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
  opacity: 0.9;
}

.confidence-container {
  position: relative;
  width: 100%;
  height: 40px;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 0.75rem;
}

.confidence-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  transition: width 0.5s ease;
}

.confidence-text {
  position: relative;
  font-weight: 700;
  font-size: 1rem;
  z-index: 1;
}

/* ==================== MODAL OVERLAY ==================== */
.modal-overlay {
  position: relative;
  width: 100%;
  margin-top: 2rem;
  background-color: transparent;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-content {
  background-color: var(--bg-white);
  border-radius: var(--radius);
  padding: 2rem;
  box-shadow: var(--shadow-lg);
  max-width: 600px;
  width: 100%;
  animation: slideDown 0.3s ease;
  border: 2px solid var(--border-color);
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-dark);
  margin: 0 0 1.5rem 0;
  text-align: center;
}

/* ==================== MODAL ACTIONS ==================== */
.modal-actions {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.modal-actions .btn {
  flex: 1;
}

.btn-success {
  background-color: var(--success-color);
  color: white;
}

.btn-success:hover {
  background-color: #059669;
}

.btn-warning {
  background-color: var(--warning-color);
  color: white;
}

.btn-warning:hover {
  background-color: #d97706;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
  width: 100%;
}

.btn-primary:hover {
  background-color: #2563eb;
}

.btn-secondary {
  background-color: var(--text-muted);
  color: white;
  width: 100%;
}

.btn-secondary:hover {
  background-color: #4b5563;
}

.btn-retrain {
  background-color: #8b5cf6;
  color: white;
}

.btn-retrain:hover {
  background-color: #7c3aed;
}

/* ==================== CORRECTION FORM ==================== */
.correction-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: var(--text-dark);
  font-size: 0.95rem;
}

.form-input {
  padding: 0.75rem 1rem;
  border: 2px solid var(--border-color);
  border-radius: var(--radius);
  font-size: 1rem;
  font-family: inherit;
  transition: var(--transition);
  background-color: #fafafa;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-color);
  background-color: var(--bg-white);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input::placeholder {
  color: var(--text-muted);
}

.form-actions {
  display: flex;
  gap: 1rem;
}

.form-actions .btn {
  flex: 1;
}

/* ==================== SUCCESS MESSAGE ==================== */
.success-message {
  text-align: center;
  padding: 1rem;
}

.success-text {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--success-color);
  margin: 0 0 0.5rem 0;
}

.success-subtitle {
  color: var(--text-muted);
  margin: 0 0 1.5rem 0;
  font-size: 0.9rem;
}

.success-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* ==================== RESPONSIVE ==================== */
@media (max-width: 768px) {
  .main-wrapper {
    padding: 1rem;
  }

  .canvas-section {
    padding: 1rem;
  }

  .prediction-box {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .controls {
    flex-direction: column;
  }

  .btn-save {
    width: 100%;
  }

  .modal-content {
    padding: 1.5rem;
    width: 95%;
  }

  .result-value {
    font-size: 2.5rem;
  }

  .section-title {
    font-size: 1.5rem;
  }
}

@media (max-width: 480px) {
  .main-wrapper {
    padding: 0.75rem;
  }

  .canvas-section {
    padding: 0.75rem;
    gap: 1rem;
  }

  .section-title {
    font-size: 1.25rem;
  }

  .modal-content {
    padding: 1rem;
  }

  .result-value {
    font-size: 2rem;
  }

  .btn {
    padding: 0.6rem 1.2rem;
    font-size: 0.85rem;
  }
}
</style>