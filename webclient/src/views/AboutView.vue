<template>
  <div class="page-wrapper">

    <div class="logo-wrapper">
      <img src="/NeuroBerry_horizontal.png" alt="NeuroBerry Logo" class="logo-image" />
    </div>

    <section class="hero-section">
      <h1 class="section-title">🍓 NeuroBerry - Madurez en frambuesas por IA</h1>
      <p class="justify-text">
        Automatizamos la identificación del estado de madurez de frambuesas en una granja real mediante Visión por Computadora.
        Partimos de miles de imágenes etiquetadas con Label Studio en 5 clases (DarkRed, Cherry Red, Orange Dot, Green y Button) para entrenar un modelo que detecta y clasifica los frutos.
        <br><br><strong>El objetivo:</strong> optimizar cosecha, calidad y trazabilidad, reduciendo costos de mano de obra y variabilidad humana.</br>
      </p>
    </section>

    <section class="research-section">
      <h2 class="section-title">Investigación y Desarrollo</h2>
      <div class="info-section">
        <div class="info-left">
          <p class="justify-text big-paragraph">
            <strong>Dataset propio en campo:</strong> capturamos imágenes en diferentes horas del día, invernaderos y ángulos.
            <br><br><strong>Etiquetado con Label Studio:</strong> anotamos miles de instancias en 5 clases estandarizadas.
            <br><br><strong>Modelo de IA:</strong> red de detección (p. ej., tipo YOLO) para localizar y clasificar cada fruto.
            <br><br><strong>Bucle de mejora continua:</strong> activo-aprendizaje (active learning), re-etiquetado selectivo y reentrenamiento periódico.
          </p>
        </div>
        <div class="info-right">
          <img src="/frambuesas_1.jpg" alt="Investigación" class="info-image" />
        </div>
      </div>
    </section>

    <section class="process-section">
      <h2 class="section-title">Nuestro Proceso</h2>
      <div class="info-section reverse">
        <div class="info-left">
          <img src="/frambuesas_2.png" alt="Proceso" class="info-image" />
        </div>
        <div class="info-right">
          <p class="justify-text big-paragraph">
            <strong>Dataset propio en campo:</strong> capturamos imágenes en diferentes horas del día, invernaderos y ángulos.
            <br><br><strong>Etiquetado con Label Studio:</strong> anotamos miles de instancias en 5 clases estandarizadas.
            <br><br><strong>Modelo de IA:</strong> red de detección (YOLO) para localizar y clasificar cada fruto.
            <br><br><strong>Bucle de mejora continua:</strong> activo-aprendizaje, re-etiquetado selectivo y reentrenamiento periódico.
          </p>
        </div>
      </div>
    </section>

    <section class="results-section">
      <h2 class="section-title">Resultados y Beneficios</h2>
      <div class="results-cards">
        <div class="card">
          <h3>Optimización</h3>
          <p>Optimizar la identificación del estado de madurez de frambuesas en una granja real</p>
        </div>
        <div class="card">
          <h3>Sostenibilidad</h3>
          <p>Reducción de costos de mano de obra y variabilidad humana.</p>
        </div>
        <div class="card">
          <h3>Progresivo</h3>
          <p>Mejora continua del modelo a través de activo-aprendizaje y reentrenamiento.</p>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup></script>

<style scoped>
.page-wrapper {
  width: 100%;
  min-height: 100vh;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Poppins', sans-serif;
  color: #333;
  display: flex;
  flex-direction: column;
  gap: 4rem;
  text-align: center;
}

.logo-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
}

.logo-image {
  max-width: 400px;
  width: 90%;
  height: auto;
  border-radius: 10px;
}

section {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.section-title {
  font-size: 2rem;
  font-weight: 800;
  color: #b22222;
}

.hero-section p {
  font-size: 1.2rem;
  line-height: 1.6;
}

.info-section {
  display: flex;
  gap: 2rem;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
}

.info-section.reverse {
  flex-direction: row-reverse;
}

.info-left, .info-right {
  flex: 1;
  min-width: 250px;
}

.justify-text {
  text-align: justify;
}

.big-paragraph {
  font-size: 1.1rem;
  line-height: 1.8;
}

.info-image {
  width: 100%;
  max-width: 400px;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.results-cards {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  flex-wrap: wrap;
}

.card {
  background-color: #fff;
  border-radius: 12px;
  padding: 1.5rem;
  width: 250px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.15);
}

.card h3 {
  color: #b22222;
  margin-bottom: 0.5rem;
}

@keyframes fadeInUp {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .info-section, .info-section.reverse {
    flex-direction: column;
    text-align: center;
  }
  .info-image {
    max-width: 100%;
    margin-top: 1rem;
  }
  .results-cards {
    flex-direction: column;
    align-items: center;
  }
  .logo-image {
    max-width: 90%;
  }
}

strong {
  font-weight: 700;
  color: #b22222;
}
</style>