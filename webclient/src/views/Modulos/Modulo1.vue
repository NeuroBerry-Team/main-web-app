<template>
  <div class="page-wrapper">
    <section class="hero-section">
      <h1 class="hero-title animated-item" style="animation-delay: 0.1s;">Arquitectura y Programación del Sistema</h1>
      <p class="hero-text animated-item" style="animation-delay: 0.2s;">
        Forjamos NeuroBerry sobre una base de agilidad, poder y diseño inteligente. Una arquitectura pensada no solo para funcionar, sino para revolucionar el futuro del agro.
      </p>
    </section>

    <div class="content-grid">
      <div 
        v-for="card in cards" 
        :key="card.title"
        class="content-section animated-item" 
        :style="{ animationDelay: card.animationDelay }"
        @click="openModal(card)"
      >
        <div class="icon-wrapper">
          <div class="section-icon">{{ card.icon }}</div>
        </div>
        <h2 class="section-title">{{ card.title }}</h2>
        <p class="section-text" v-html="card.text"></p>
      </div>
    </div>

    <div v-if="selectedCard" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <button class="modal-close-button" @click="closeModal">&times;</button>
        <div class="icon-wrapper">
          <div class="section-icon">{{ selectedCard.icon }}</div>
        </div>
        <h2 class="section-title">{{ selectedCard.title }}</h2>
        <p class="section-text" v-html="selectedCard.text"></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// State for the modal
const selectedCard = ref(null);

// Card data - makes the template cleaner
const cards = ref([
  {
    icon: '🔄',
    title: 'Velocidad y Adaptación',
    text: 'Innovamos en ciclos rápidos, llevando la tecnología directamente al campo. Este modelo nos permite adaptarnos, aprender y entregar valor real y tangible.',
    animationDelay: '0.3s'
  },
  {
    icon: '🏗️',
    title: 'Potencia y Simplicidad',
    text: 'Combinamos la potencia de <strong>Python</strong> con la fluidez de <strong>Vue.js</strong>. ¿El resultado? Una plataforma robusta por dentro y asombrosamente intuitiva por fuera.',
    animationDelay: '0.4s'
  },
  {
    icon: '🗃️',
    title: 'Construido para Crecer',
    text: 'No dejamos nada al azar. Cada función fue planificada estratégicamente y soportada por una base de datos escalable, garantizando un sistema fiable y preparado para los desafíos del futuro.',
    animationDelay: '0.5s'
  }
]);

// Functions to open and close the modal
const openModal = (card) => {
  selectedCard.value = card;
};

const closeModal = () => {
  selectedCard.value = null;
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');

/* --- General Page Styles --- */
.page-wrapper {
  width: 100%;
  min-height: 100vh;
  padding: 2rem;
  padding-top: 7rem;
  font-family: 'Poppins', sans-serif;
  color: #333;
  background-color: #ffffff; /* Pure white background */
}

/* --- Hero Section --- */
.hero-section {
  max-width: 1200px;
  margin: 0 auto 4rem auto;
  padding: 4rem 2rem;
  border-radius: 20px;
  text-align: center;
  background: linear-gradient(135deg, #e52d27, #b31217);
  color: white;
  box-shadow: 0 10px 40px rgba(185, 28, 28, 0.25);
}
.hero-title { font-size: 2.8rem; font-weight: 800; text-shadow: 0 3px 6px rgba(0,0,0,0.2); }
.hero-text { color: rgba(255, 255, 255, 0.9); font-size: 1.2rem; margin-top: 1.5rem; max-width: 800px; margin-left: auto; margin-right: auto; line-height: 1.6; }

/* --- Content Grid & Cards --- */
.content-grid {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 2.5rem;
}
.content-section {
  background-color: #ffffff;
  border-radius: 18px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.07);
  padding: 2.5rem;
  text-align: center;
  border: 1px solid #e5e7eb;
  border-bottom: 4px solid transparent;
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
  display: flex;
  flex-direction: column;
  cursor: pointer; /* Indicates clickable */
}
.content-section:hover {
  transform: translateY(-12px);
  box-shadow: 0 20px 40px -5px rgba(0,0,0,0.12);
  border-bottom-color: #c31432;
}

/* --- Card Elements --- */
.icon-wrapper {
  margin: 0 auto 1.5rem auto;
  background: linear-gradient(135deg, #e52d27, #b31217);
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 5px 15px rgba(195, 20, 50, 0.4);
  animation: pulse 2.5s infinite cubic-bezier(0.4, 0, 0.6, 1);
  flex-shrink: 0; /* Prevents icon from shrinking */
}
.section-icon { font-size: 2.5rem; color: white; }
.section-title { font-size: 1.5rem; font-weight: 700; color: #b91c1c; margin-bottom: 1rem; }
.section-text { font-size: 1rem; line-height: 1.7; color: #555; flex-grow: 1; }
.section-text:deep(strong) { color: #c31432; font-weight: 600; }

/* --- Modal Styles --- */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(5px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}
.modal-content {
  background: #ffffff;
  padding: 3rem;
  border-radius: 20px;
  max-width: 600px;
  width: 90%;
  text-align: center;
  position: relative;
  box-shadow: 0 10px 50px rgba(0,0,0,0.3);
  animation: scaleIn 0.3s ease;
}
.modal-close-button {
  position: absolute;
  top: 15px;
  right: 20px;
  background: none;
  border: none;
  font-size: 2.5rem;
  color: #aaa;
  cursor: pointer;
  line-height: 1;
  transition: color 0.2s ease;
}
.modal-close-button:hover { color: #333; }
/* Reuse styles inside the modal */
.modal-content .section-title { font-size: 1.8rem; }
.modal-content .section-text { font-size: 1.1rem; line-height: 1.8; }

/* --- Animations --- */
.animated-item { opacity: 0; animation: fadeInUp 0.7s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards; }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
@keyframes pulse { 0% { transform: scale(1); box-shadow: 0 5px 15px rgba(195, 20, 50, 0.4); } 50% { transform: scale(1.05); box-shadow: 0 8px 25px rgba(195, 20, 50, 0.6); } 100% { transform: scale(1); box-shadow: 0 5px 15px rgba(195, 20, 50, 0.4); } }

/* Modal animations */
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes scaleIn { from { opacity: 0; transform: scale(0.9); } to { opacity: 1; transform: scale(1); } }

/* Responsive adjustments */
@media (max-width: 768px) {
  .hero-title { font-size: 2.2rem; }
  .hero-text { font-size: 1.1rem; }
  .modal-content { padding: 2rem; }
  .modal-content .section-title { font-size: 1.5rem; }
  .modal-content .section-text { font-size: 1rem; }
}
</style>