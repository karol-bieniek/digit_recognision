<script setup>

import { ref, onMounted } from 'vue';
import { sendImgDigit, saveCanvas, retrain } from '../../api/predict.ts';
import Canvas from './Canvas.vue';
import { getCanvasBlob } from '../utils';



// Predykcje modelu 
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


// Wysyłanie rysunku do backendu
const uploadImage = async () => {
  const canvas = canvasActions.value.getCanvas();
  try {
      const imageBlob = await getCanvasBlob(canvas);
      const formData = new FormData();
      formData.append('drawing', imageBlob, 'rysunek-uzytkownika.png');

      const response = await sendImgDigit(formData);
      if (response !== null) {
        prediction.value = response.prediction;
        confidence.value = response.confidence;
      } else {
        alert('Błąd podczas wysyłania (Serwer zwrócił błąd).');
      }

  } catch (error) {
    console.error('Błąd sieci:', error);
  }
};


const handleYes = async () => {
  const canvas = canvasActions.value.getCanvas();
  const imageBlob = await getCanvasBlob(canvas);

  const formData = new FormData();
  formData.append('drawing', imageBlob, 'rysunek-uzytkownika.png');
  formData.append('prediction', prediction.value);
  formData.append('confidence', confidence.value);
  const correctDigit = prediction.value; // Jeśli użytkownik potwierdza, to poprawna cyfra to ta, którą przewidział model
  formData.append('correct_digit', correctDigit);
  

  try {
      const response = await saveCanvas(formData);
      if (response === null) {
          alert("Błąd serwera");
      } else {
        console.log("Predykcja zapisana w bazie danych");
      }
  } catch (error) {
      console.error('Błąd sieci:', error);
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
    alert("Nie przepowadzaono predykcji!");
    return;
  }


  const canvas = canvasActions.value.getCanvas();
  try {
    const imageBlob = await getCanvasBlob(canvas);
    const formData = new FormData();
    formData.append('drawing', imageBlob, 'rysunek.png');
    formData.append('prediction', prediction.value);
    formData.append('confidence', confidence.value);
    formData.append('correct_digit', correctNumber.value);

    const response = await saveCanvas(formData);
    if (response === null) {
      alert("Błąd serwera");
    } else {
      isReview.value = false;
      isSuccess.value = true;
    }
  } catch (error) {
    console.error('Błąd sieci:', error);
  }
}


const handleRetrain = async () => {
  isRetraining.value = true; 
  try {
    await retrain();
  } catch (error) {
    console.log("Błąd przy trenowaniu: ", error);
  } finally {
    isRetraining.value = false; 
  }
}

</script>

<template>
  <div class="main-wrapper">
    <!-- Sekcja kanwy i rysowania -->
    <div class="canvas-section">
      <h2 class="section-title">Rozpoznawanie Cyfr</h2>
      <p class="subtitle">Narysuj cyfrę myszką na płótnie poniżej</p>
      
      <Canvas ref="canvasActions" class="canvas-element"/>

      <!-- Przyciski kontroli kanwy -->
      <div class="controls">
        <button @click="clearCanvas" class="btn btn-clear">
          <span class="btn-icon">✕</span> Wyczyść
        </button>
        <button @click="uploadImage" class="btn btn-save">
          <span class="btn-icon">✓</span> Wyślij do analizy
        </button>
      </div>

      <!-- Wyniki predykcji -->
      <div class="prediction-section" v-if="prediction !== null">
        <div class="prediction-box">
          <div class="prediction-result">
            <span class="result-label">Rozpoznana cyfra:</span>
            <span class="result-value">{{ prediction }}</span>
          </div>
          <div class="confidence-bar">
            <span class="confidence-label">Pewność predykcji:</span>
            <div class="confidence-container">
              <div class="confidence-fill" :style="{ width: confidence + '%' }"></div>
              <span class="confidence-text">{{ confidence }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal oceny predykcji -->
    <div class="modal-overlay" v-if="prediction !== null">
      <div class="modal-content">

        <h3 class="modal-title" v-if="!isReview && !isSuccess">Czy cyfra została rozpoznana poprawnie?</h3>
        <!-- Przyciski Tak/Nie -->
        <div class="modal-actions" v-if="!isReview && !isSuccess">

          <button type="button" @click="handleYes" class="btn btn-success">Tak, jest OK</button>
          <button type="button" @click="handleNo" class="btn btn-warning">Nie, popraw</button>
        </div>

        <!-- Formularz korekty -->
        <form @submit.prevent="handleReview" v-if="isReview" class="correction-form">
          <div class="form-group">
            <label for="correct-number">Jaka cyfra powinna być rozpoznana?</label>
            <input 
              id="correct-number" 
              v-model.number="correctNumber" 
              type="number" 
              min="0"
              max="9"
              placeholder="Wpisz cyfrę (0-9)"
              class="form-input"
            />
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary">Prześlij korektę</button>
            <button type="button" @click="isReview = false" class="btn btn-secondary">Anuluj</button>
          </div>
        </form>

        <!-- Potwierdzenie sukcesu -->
        <div class="success-message" v-if="isSuccess">
          <p class="success-text">✓ Dziękujemy za potwierdzenie!</p>
          <p class="success-subtitle">Twoja ocena pomaga w trenowaniu modelu</p>
          <div class="success-actions">
            <button type="button" @click="isSuccess = false; prediction = null" class="btn btn-primary">Zamknij</button>
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
          <span v-if="!isRetraining">Przetrenuj model</span>
          <span v-else>Trenowanie...</span>
        </button>
      </div>
  </div>
</template>


<style scoped>
/* ==================== GŁÓWNY KONTENER ==================== */
.main-wrapper {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  background-color: var(--bg-light);
  min-height: 100vh;
}

/* ==================== SEKCJA KANWY ==================== */
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

/* ==================== ELEMENT KANWY ==================== */
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

/* ==================== PRZYCISKI ==================== */
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

/* ==================== SEKCJA PREDYKCJI ==================== */
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

/* Wynik predykcji */
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

/* Pasek pewności */
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

/* ==================== AKCJE MODALU ==================== */
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

/* ==================== FORMULARZ KOREKTY ==================== */
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

/* ==================== KOMUNIKAT SUKCESU ==================== */
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