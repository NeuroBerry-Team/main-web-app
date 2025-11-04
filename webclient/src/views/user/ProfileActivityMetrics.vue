<template>
  <Teleport to="body">
    <div class="modal-overlay" @click.self="$router.push('/profile')">
      <div class="modal-container" @click.stop>
        <!-- Header -->
        <div class="metrics-header-modal">
          <div class="header-content">
            <h1 class="header-title">📊 Métricas de Análisis</h1>
            <p class="header-subtitle">Estadísticas detalladas de tus detecciones</p>
          </div>
          <div class="header-actions">
            <button @click="$router.push('/profile')" class="btn-close">✕</button>
          </div>
        </div>

        <!-- Content -->
        <div class="modal-content-scroll">
          <!-- Loading State -->
          <div v-if="initialLoading" class="loading-container">
            <div class="spinner"></div>
            <p>Cargando métricas...</p>
          </div>

          <!-- Error State -->
          <div v-else-if="error" class="error-container">
            <p class="error-message">⚠️ {{ error }}</p>
            <button @click="$router.push('/profile')" class="btn-secondary">Cerrar</button>
          </div>

          <!-- Metrics Content -->
          <div v-else class="metrics-content">
            <!-- Summary Cards -->
            <div class="summary-grid">
              <div class="summary-card">
                <div class="card-icon">🔬</div>
                <div class="card-content">
                  <div class="card-value">{{ totalInferences }}</div>
                  <div class="card-label">Total de Análisis</div>
                </div>
              </div>

              <div class="summary-card">
                <div class="card-icon">🎯</div>
                <div class="card-content">
                  <div class="card-value">{{ totalDetections }}</div>
                  <div class="card-label">Total de Detecciones</div>
                </div>
              </div>

              <div class="summary-card">
                <div class="card-icon">📈</div>
                <div class="card-content">
                  <div class="card-value">{{ recentInferences }}</div>
                  <div class="card-label">Análisis Recientes</div>
                  <div class="card-hint">Realizados en los últimos 30 días</div>
                </div>
              </div>

              <div class="summary-card">
                <div class="card-icon">📊</div>
                <div class="card-content">
                  <div class="card-value">{{ avgDetectionsPerInference }}</div>
                  <div class="card-label">Detecciones Promedio</div>
                  <div class="card-hint">Por cada análisis realizado</div>
                </div>
              </div>
            </div>

            <!-- Class Distribution Charts -->
            <div class="charts-grid">
              <!-- Bar Chart -->
              <div class="chart-card">
                <div class="chart-header">
                  <h3 class="chart-title">Distribución por Clase</h3>
                  <p class="chart-subtitle">Conteo total de detecciones</p>
                </div>
                <div class="chart-body">
                  <canvas ref="barChartCanvas" v-if="hasClassData"></canvas>
                  <div v-else class="no-data">
                    <span class="text-4xl">📊</span>
                    <p>No hay datos disponibles</p>
                  </div>
                </div>
              </div>

              <!-- Pie Chart -->
              <div class="chart-card">
                <div class="chart-header">
                  <h3 class="chart-title">Proporción de Clases</h3>
                  <p class="chart-subtitle">Porcentaje por tipo</p>
                </div>
                <div class="chart-body">
                  <canvas ref="pieChartCanvas" v-if="hasClassData"></canvas>
                  <div v-else class="no-data">
                    <span class="text-4xl">🥧</span>
                    <p>No hay datos disponibles</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Time Series Chart -->
            <div class="chart-card chart-full-width">
              <div class="chart-header">
                <div>
                  <h3 class="chart-title">Evolución Temporal</h3>
                  <p class="chart-subtitle">Detecciones a lo largo del tiempo</p>
                </div>
                <div class="chart-controls">
                  <select v-model="timeGrouping" @change="loadTimeSeriesData" class="time-select">
                    <option value="day">Por Día</option>
                    <option value="week">Por Semana</option>
                    <option value="month">Por Mes</option>
                  </select>
                  <select v-model="timePeriod" @change="loadTimeSeriesData" class="time-select">
                    <option value="7">7 días</option>
                    <option value="30">30 días</option>
                    <option value="60">60 días</option>
                    <option value="90">90 días</option>
                  </select>
                </div>
              </div>
              <div class="chart-body">
                <canvas ref="lineChartCanvas" v-if="hasTimeSeriesData"></canvas>
                <div v-else class="no-data">
                  <span class="text-4xl">📈</span>
                  <p>No hay datos de series temporales</p>
                </div>
              </div>
            </div>

            <!-- Class Details Table -->
            <div class="chart-card chart-full-width">
              <div class="chart-header">
                <h3 class="chart-title">Detalle por Clase</h3>
                <p class="chart-subtitle">Estadísticas completas de cada clase</p>
              </div>
              <div class="table-container">
                <table class="class-table" v-if="hasClassData">
                  <thead>
                    <tr>
                      <th>Clase</th>
                      <th>Total</th>
                      <th>Porcentaje</th>
                      <th>Distribución</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(count, classId) in sortedClassCounts" :key="classId">
                      <td>
                        <div class="class-label">
                          <span class="class-dot" :style="{ backgroundColor: getClassColor(classId) }"></span>
                          {{ getClassLabel(classId) }}
                        </div>
                      </td>
                      <td class="text-bold">{{ count }}</td>
                      <td>{{ getClassPercentage(classId) }}%</td>
                      <td>
                        <div class="progress-bar">
                          <div 
                            class="progress-fill" 
                            :style="{ 
                              width: getClassPercentage(classId) + '%',
                              backgroundColor: getClassColor(classId)
                            }"
                          ></div>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <div v-else class="no-data">
                  <p>No hay datos de clases disponibles</p>
                </div>
              </div>
            </div>

            <!-- Harvest Estimation Tool -->
            <div class="chart-card chart-full-width harvest-tool-card">
              <div class="chart-header harvest-tool-header" @click="toggleHarvestTool">
                <div>
                  <h3 class="chart-title">🌾 Estimador de Cosecha</h3>
                  <p class="chart-subtitle">Calcula producción estimada según parámetros de cultivo</p>
                </div>
                <button class="toggle-btn" :class="{ 'expanded': showHarvestTool }">
                  {{ showHarvestTool ? '▼' : '▶' }}
                </button>
              </div>
              
              <transition name="harvest-expand">
                <div v-if="showHarvestTool" class="harvest-tool-content">
                  <!-- Input Parameters -->
                  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mb-8 p-4 md:p-6 bg-white rounded-xl border border-gray-200">
                    <div class="input-group">
                      <label for="timeRange" class="block font-semibold text-gray-700 text-sm md:text-base mb-2">Período de Análisis</label>
                      <select 
                        id="timeRange" 
                        v-model="harvestParams.timeRange"
                        @change="calculateHarvest"
                        class="w-full px-3 py-2 md:py-3 border-2 border-gray-200 rounded-lg text-sm md:text-base bg-white cursor-pointer transition-all focus:outline-none focus:border-red-700 focus:ring-4 focus:ring-red-700/10"
                      >
                        <option value="1">Último día</option>
                        <option value="3">Últimos 3 días</option>
                        <option value="7" selected>Última semana</option>
                        <option value="14">Últimas 2 semanas</option>
                        <option value="30">Último mes</option>
                      </select>
                      <span class="block mt-1 text-xs md:text-sm text-gray-500 italic">Solo se consideran análisis recientes</span>
                    </div>

                    <div class="input-group">
                      <label for="totalMeters" class="block font-semibold text-gray-700 text-sm md:text-base mb-2">Metros Totales de Cultivo</label>
                      <input 
                        type="number" 
                        id="totalMeters" 
                        v-model.number="harvestParams.totalMeters"
                        @input="calculateHarvest"
                        placeholder="200"
                        min="1"
                        step="1"
                        class="w-full px-3 py-2 md:py-3 border-2 border-gray-200 rounded-lg text-sm md:text-base transition-all focus:outline-none focus:border-red-700 focus:ring-4 focus:ring-red-700/10"
                      />
                      <span class="block mt-1 text-xs md:text-sm text-gray-500 italic">Metros lineales totales de tu campo</span>
                    </div>

                    <div class="input-group">
                      <label for="samplingPercentage" class="block font-semibold text-gray-700 text-sm md:text-base mb-2">
                        % del Cultivo Analizado: <strong>{{ harvestParams.samplingPercentage }}%</strong>
                      </label>
                      <input 
                        type="range" 
                        id="samplingPercentage" 
                        v-model.number="harvestParams.samplingPercentage"
                        @input="calculateHarvest"
                        min="5"
                        max="100"
                        step="5"
                        class="harvest-slider w-full"
                      />
                      <div class="slider-labels">
                        <span>5%</span>
                        <span>50%</span>
                        <span>100%</span>
                      </div>
                      <span class="block mt-1 text-xs md:text-sm text-gray-500 italic">¿Qué porcentaje analizaste?</span>
                    </div>
                    
                    <div class="input-group">
                      <label for="unitaryWeight" class="block font-semibold text-gray-700 text-sm md:text-base mb-2">Peso Unitario (gramos)</label>
                      <input 
                        type="number" 
                        id="unitaryWeight" 
                        v-model.number="harvestParams.unitaryWeight"
                        @input="calculateHarvest"
                        placeholder="4.5"
                        min="0"
                        step="0.1"
                        class="w-full px-3 py-2 md:py-3 border-2 border-gray-200 rounded-lg text-sm md:text-base transition-all focus:outline-none focus:border-red-700 focus:ring-4 focus:ring-red-700/10"
                      />
                      <span class="block mt-1 text-xs md:text-sm text-gray-500 italic">Peso promedio por frambuesa</span>
                    </div>
                  </div>

                  <!-- Harvest Timeline Results -->
                  <div v-if="harvestEstimate.isValid" class="harvest-timeline">
                    <div class="harvest-info">
                      📊 Basado en <strong>{{ harvestEstimate.analyzedInferences }}</strong> análisis 
                      de <strong>{{ harvestParams.samplingPercentage }}%</strong> 
                      (<strong>{{ (harvestParams.totalMeters * harvestParams.samplingPercentage / 100).toFixed(1) }}m</strong>) 
                      de <strong>{{ harvestParams.totalMeters }}m</strong> totales
                      en los últimos <strong>{{ harvestParams.timeRange }}</strong> días
                    </div>

                    <div class="timeline-item today">
                      <div class="timeline-header">
                        <span class="timeline-icon">🍓</span>
                        <span class="timeline-label">HOY - Listo para Cosechar</span>
                      </div>
                      <div class="timeline-content">
                        <div class="harvest-result primary">
                          <span class="result-value">{{ harvestEstimate.today.fresh }} kg</span>
                          <span class="result-label">Consumo Fresco (C4 Rojo Brillante)</span>
                          <span class="result-count">{{ harvestEstimate.filteredCounts['3'] || 0 }} frambuesas</span>
                        </div>
                        <div class="harvest-result secondary">
                          <span class="result-value">{{ harvestEstimate.today.jam }} kg</span>
                          <span class="result-label">Mermelada (C5 Rojo Oscuro)</span>
                          <span class="result-count">{{ harvestEstimate.filteredCounts['4'] || 0 }} frambuesas</span>
                        </div>
                      </div>
                    </div>

                    <div class="timeline-item">
                      <div class="timeline-header">
                        <span class="timeline-icon">🟠</span>
                        <span class="timeline-label">EN 3 DÍAS</span>
                      </div>
                      <div class="timeline-content">
                        <div class="harvest-result">
                          <span class="result-value">{{ harvestEstimate.in3Days }} kg</span>
                          <span class="result-label">Maduración (C3 Naranja)</span>
                          <span class="result-count">{{ harvestEstimate.filteredCounts['2'] || 0 }} frambuesas</span>
                        </div>
                      </div>
                    </div>

                    <div class="timeline-item">
                      <div class="timeline-header">
                        <span class="timeline-icon">🟢</span>
                        <span class="timeline-label">EN 1 SEMANA</span>
                      </div>
                      <div class="timeline-content">
                        <div class="harvest-result">
                          <span class="result-value">{{ harvestEstimate.in1Week }} kg</span>
                          <span class="result-label">Verde (C2 Verde)</span>
                          <span class="result-count">{{ harvestEstimate.filteredCounts['1'] || 0 }} frambuesas</span>
                        </div>
                      </div>
                    </div>

                    <div class="timeline-item">
                      <div class="timeline-header">
                        <span class="timeline-icon">⚪</span>
                        <span class="timeline-label">EN 2 SEMANAS</span>
                      </div>
                      <div class="timeline-content">
                        <div class="harvest-result">
                          <span class="result-value">{{ harvestEstimate.in2Weeks }} kg</span>
                          <span class="result-label">Botón (C1 Botón)</span>
                          <span class="result-count">{{ harvestEstimate.filteredCounts['0'] || 0 }} frambuesas</span>
                        </div>
                      </div>
                    </div>

                    <!-- Total Summary -->
                    <div class="harvest-total">
                      <div class="total-label">Producción Total Estimada:</div>
                      <div class="total-value">{{ harvestEstimate.total }} kg</div>
                    </div>

                    <!-- Harvest Timeline Chart -->
                    <div class="harvest-chart-container">
                      <h4 class="chart-subtitle">📊 Visualización del Calendario de Cosecha</h4>
                      <canvas ref="harvestChartCanvas"></canvas>
                    </div>

                    <div class="harvest-disclaimer">
                      <strong>Nota:</strong> Esta es una estimación basada en las detecciones actuales. 
                      Los tiempos de maduración pueden variar según condiciones climáticas.
                    </div>
                  </div>

                  <div v-else class="harvest-empty">
                    <p>👆 Ingresa los parámetros de tu cultivo para ver la estimación</p>
                  </div>
                </div>
              </transition>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import { useMetrics } from '../../composables/use_metrics.js';
import Chart from 'chart.js/auto';

const { 
  loading, 
  error, 
  classDetectionMetrics, 
  timeSeriesMetrics,
  summaryMetrics,
  getClassDetectionMetrics, 
  getTimeSeriesMetrics,
  getSummaryMetrics,
  getClassLabel, 
  getClassColor 
} = useMetrics();

const initialLoading = ref(true);
const barChartCanvas = ref(null);
const pieChartCanvas = ref(null);
const lineChartCanvas = ref(null);
const harvestChartCanvas = ref(null);

let barChart = null;
let pieChart = null;
let lineChart = null;
let harvestChart = null;

// Time series controls
const timeGrouping = ref('day');
const timePeriod = ref('30');

// Harvest estimation tool
const showHarvestTool = ref(false);
const harvestParams = ref({
  timeRange: 7,
  totalMeters: null,
  samplingPercentage: 20,  // Default: user analyzed 20% of their field
  unitaryWeight: null
});

const harvestEstimate = ref({
  isValid: false,
  today: { fresh: 0, jam: 0 },
  in3Days: 0,
  in1Week: 0,
  in2Weeks: 0,
  total: 0,
  analyzedInferences: 0
});

function toggleHarvestTool() {
  showHarvestTool.value = !showHarvestTool.value;
  
  // Clear data when closing
  if (!showHarvestTool.value) {
    harvestParams.value = {
      timeRange: 7,
      totalMeters: null,
      samplingPercentage: 20,
      unitaryWeight: null
    };
    harvestEstimate.value = {
      isValid: false,
      today: { fresh: 0, jam: 0 },
      in3Days: 0,
      in1Week: 0,
      in2Weeks: 0,
      total: 0,
      analyzedInferences: 0
    };
    // Destroy chart
    if (harvestChart) {
      harvestChart.destroy();
      harvestChart = null;
    }
  }
}

function getFilteredCounts() {
  if (!classDetectionMetrics.value?.inferenceHistory) {
    return null;
  }

  const { timeRange } = harvestParams.value;
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - timeRange);

  // Filter inferences by date
  const recentInferences = classDetectionMetrics.value.inferenceHistory.filter(inference => {
    if (!inference.date) return false;
    const inferenceDate = new Date(inference.date);
    return inferenceDate >= cutoffDate;
  });

  // Count detections from recent inferences only
  const filteredCounts = {
    '0': 0,
    '1': 0,
    '2': 0,
    '3': 0,
    '4': 0
  };

  recentInferences.forEach(inference => {
    if (inference.classCounts) {
      Object.entries(inference.classCounts).forEach(([classId, count]) => {
        const key = classId.toString();
        filteredCounts[key] = (filteredCounts[key] || 0) + count;
      });
    }
  });

  return {
    counts: filteredCounts,
    inferenceCount: recentInferences.length
  };
}

function calculateHarvest() {
  const { totalMeters, samplingPercentage, unitaryWeight } = harvestParams.value;
  
  // Validate inputs
  if (!totalMeters || !samplingPercentage || !unitaryWeight || 
      totalMeters <= 0 || samplingPercentage <= 0 || unitaryWeight <= 0) {
    harvestEstimate.value.isValid = false;
    return;
  }

  const filtered = getFilteredCounts();
  if (!filtered || filtered.inferenceCount === 0) {
    harvestEstimate.value.isValid = false;
    return;
  }

  const counts = filtered.counts;
  
  // Calculate kg for each class
  const calculateKg = (count) => {
    if (!count) return '0.00';
    const analyzedMeters = totalMeters * (samplingPercentage / 100);
    const densityPerMeter = count / analyzedMeters; // raspberries per meter
    const totalRaspberries = densityPerMeter * totalMeters;
    const totalGrams = totalRaspberries * unitaryWeight;
    return (totalGrams / 1000).toFixed(2);
  };

  // Harvest schedule based on maturity
  // Class IDs: 0=C1 Boton, 1=C2 Green, 2=C3 Orange, 3=C4 BrightRed, 4=C5 DarkRed
  const freshKg = calculateKg(counts['3'] || 0);   // C4 BrightRed (class_id 3) - ready today
  const jamKg = calculateKg(counts['4'] || 0);     // C5 DarkRed (class_id 4) - overripe, for jam
  const in3DaysKg = calculateKg(counts['2'] || 0); // C3 Orange (class_id 2) - 3 days
  const in1WeekKg = calculateKg(counts['1'] || 0); // C2 Green (class_id 1) - 7 days
  const in2WeeksKg = calculateKg(counts['0'] || 0); // C1 Button (class_id 0) - 14 days

  const total = (
    parseFloat(freshKg) + 
    parseFloat(jamKg) + 
    parseFloat(in3DaysKg) + 
    parseFloat(in1WeekKg) + 
    parseFloat(in2WeeksKg)
  ).toFixed(2);

  harvestEstimate.value = {
    isValid: true,
    today: {
      fresh: freshKg,
      jam: jamKg
    },
    in3Days: in3DaysKg,
    in1Week: in1WeekKg,
    in2Weeks: in2WeeksKg,
    total: total,
    analyzedInferences: filtered.inferenceCount,
    filteredCounts: counts
  };

  // Create chart after data is ready
  nextTick(() => {
    createHarvestChart();
  });
}

function createHarvestChart() {
  if (!harvestChartCanvas.value || !harvestEstimate.value.isValid) {
    return;
  }

  const ctx = harvestChartCanvas.value.getContext('2d');

  if (harvestChart) {
    harvestChart.destroy();
  }

  // Prepare data for stacked bar chart
  const labels = ['Hoy', 'En 3 días', 'En 1 semana', 'En 2 semanas'];
  const freshData = [
    parseFloat(harvestEstimate.value.today.fresh),
    0,
    0,
    0
  ];
  const jamData = [
    parseFloat(harvestEstimate.value.today.jam),
    0,
    0,
    0
  ];
  const ripening = [
    0,
    parseFloat(harvestEstimate.value.in3Days),
    parseFloat(harvestEstimate.value.in1Week),
    parseFloat(harvestEstimate.value.in2Weeks)
  ];

  harvestChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Consumo Fresco (C4)',
          data: freshData,
          backgroundColor: '#dc2626',
          borderColor: '#991b1b',
          borderWidth: 1
        },
        {
          label: 'Mermelada (C5)',
          data: jamData,
          backgroundColor: '#f59e0b',
          borderColor: '#d97706',
          borderWidth: 1
        },
        {
          label: 'En Maduración',
          data: ripening,
          backgroundColor: '#16a34a',
          borderColor: '#15803d',
          borderWidth: 1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top'
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 12,
          callbacks: {
            label: function(context) {
              return `${context.dataset.label}: ${context.parsed.y} kg`;
            }
          }
        }
      },
      scales: {
        x: {
          stacked: true,
          grid: {
            display: false
          }
        },
        y: {
          stacked: true,
          beginAtZero: true,
          ticks: {
            callback: function(value) {
              return value + ' kg';
            }
          },
          title: {
            display: true,
            text: 'Kilogramos Estimados'
          }
        }
      }
    }
  });
}

// Computed properties
const totalInferences = computed(() => {
  return classDetectionMetrics.value?.totalInferences || 0;
});

const totalDetections = computed(() => {
  return classDetectionMetrics.value?.totalDetections || 0;
});

const recentInferences = computed(() => {
  return summaryMetrics.value?.recentInferences || 0;
});

const avgDetectionsPerInference = computed(() => {
  if (totalInferences.value === 0) return 0;
  return (totalDetections.value / totalInferences.value).toFixed(1);
});

const hasClassData = computed(() => {
  return classDetectionMetrics.value && 
         classDetectionMetrics.value.classCounts && 
         Object.keys(classDetectionMetrics.value.classCounts).length > 0;
});

const hasTimeSeriesData = computed(() => {
  return timeSeriesMetrics.value && 
         timeSeriesMetrics.value.timeSeries && 
         timeSeriesMetrics.value.timeSeries.length > 0;
});

const sortedClassCounts = computed(() => {
  if (!hasClassData.value) return {};
  
  const counts = classDetectionMetrics.value.classCounts;
  const sorted = Object.entries(counts)
    .sort(([, a], [, b]) => b - a)
    .reduce((acc, [key, val]) => {
      acc[key] = val;
      return acc;
    }, {});
  
  return sorted;
});

function getClassPercentage(classId) {
  if (!classDetectionMetrics.value || !classDetectionMetrics.value.classPercentages) {
    return 0;
  }
  return classDetectionMetrics.value.classPercentages[classId] || 0;
}

async function loadTimeSeriesData() {
  try {
    await getTimeSeriesMetrics(timeGrouping.value, parseInt(timePeriod.value));
    await nextTick();
    updateLineChart();
  } catch (err) {
    console.error('Error loading time series data:', err);
  }
}

function createBarChart() {
  if (!barChartCanvas.value || !hasClassData.value) {
    return;
  }

  const ctx = barChartCanvas.value.getContext('2d');
  const counts = classDetectionMetrics.value.classCounts;
  
  const labels = Object.keys(counts).map(id => getClassLabel(id));
  const data = Object.values(counts);
  const colors = Object.keys(counts).map(id => getClassColor(id));

  if (barChart) {
    barChart.destroy();
  }

  barChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Detecciones',
        data: data,
        backgroundColor: colors,
        borderColor: colors,
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 12,
          titleFont: {
            size: 14
          },
          bodyFont: {
            size: 13
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            precision: 0
          }
        }
      }
    }
  });
}

function createPieChart() {
  if (!pieChartCanvas.value || !hasClassData.value) {
    return;
  }

  const ctx = pieChartCanvas.value.getContext('2d');
  const counts = classDetectionMetrics.value.classCounts;
  
  const labels = Object.keys(counts).map(id => getClassLabel(id));
  const data = Object.values(counts);
  const colors = Object.keys(counts).map(id => getClassColor(id));

  if (pieChart) {
    pieChart.destroy();
  }

  pieChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: colors,
        borderColor: '#fff',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            padding: 15,
            font: {
              size: 12
            }
          }
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 12,
          callbacks: {
            label: function(context) {
              const label = context.label || '';
              const value = context.parsed || 0;
              const total = context.dataset.data.reduce((a, b) => a + b, 0);
              const percentage = ((value / total) * 100).toFixed(1);
              return `${label}: ${value} (${percentage}%)`;
            }
          }
        }
      }
    }
  });
}

function updateLineChart() {
  if (!lineChartCanvas.value || !hasTimeSeriesData.value) return;

  const ctx = lineChartCanvas.value.getContext('2d');
  const timeSeries = timeSeriesMetrics.value.timeSeries;
  
  const labels = timeSeries.map(item => {
    const date = new Date(item.date);
    if (timeGrouping.value === 'month') {
      return date.toLocaleDateString('es-ES', { year: 'numeric', month: 'short' });
    } else if (timeGrouping.value === 'week') {
      return date.toLocaleDateString('es-ES', { month: 'short', day: 'numeric' });
    } else {
      return date.toLocaleDateString('es-ES', { month: 'short', day: 'numeric' });
    }
  });
  
  const totalDetections = timeSeries.map(item => item.totalDetections);

  if (lineChart) {
    lineChart.destroy();
  }

  lineChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Total de Detecciones',
        data: totalDetections,
        borderColor: '#b91c1c',
        backgroundColor: 'rgba(185, 28, 28, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointBackgroundColor: '#b91c1c',
        pointBorderColor: '#fff',
        pointBorderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top'
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 12,
          titleFont: {
            size: 14
          },
          bodyFont: {
            size: 13
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            precision: 0
          }
        },
        x: {
          ticks: {
            maxRotation: 45,
            minRotation: 45
          }
        }
      }
    }
  });
}

onMounted(async () => {
  try {
    initialLoading.value = true;
    await Promise.all([
      getClassDetectionMetrics(),
      getSummaryMetrics(),
      loadTimeSeriesData()
    ]);
    initialLoading.value = false;
    await nextTick();
    await nextTick();
    setTimeout(() => {
      createBarChart();
      createPieChart();
      updateLineChart();
    }, 100);
  } catch (err) {
    console.error('Error loading metrics:', err);
    initialLoading.value = false;
  }
});
</script>

<style scoped>
/* Modal Base */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}

.modal-container {
  background-color: white;
  border-radius: 24px;
  width: 100%;
  max-width: 1400px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  overflow: hidden;
}

/* Header */
.metrics-header-modal {
  background: linear-gradient(135deg, #b91c1c 0%, #dc2626 100%);
  padding: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid rgba(255, 255, 255, 0.1);
}

.header-content {
  flex: 1;
}

.header-title {
  font-size: 2rem;
  font-weight: bold;
  color: white;
  margin: 0;
}

.header-subtitle {
  color: rgba(255, 255, 255, 0.9);
  margin-top: 0.5rem;
  font-size: 0.95rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.btn-close {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1.5rem;
  line-height: 1;
}

.btn-close:hover {
  background-color: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

/* Scrollable Content */
.modal-content-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  background-color: #f9fafb;
}

/* Loading & Error States */
.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.spinner {
  border: 4px solid rgba(185, 28, 28, 0.1);
  border-left-color: #b91c1c;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.error-message {
  color: #dc2626;
  font-size: 1.1rem;
  margin-bottom: 1rem;
}

.btn-secondary {
  background-color: #b91c1c;
  color: white;
  border: none;
  border-radius: 12px;
  padding: 0.75rem 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
}

.btn-secondary:hover {
  background-color: #991b1b;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(185, 28, 28, 0.3);
}

/* Metrics Content */
.metrics-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Summary Cards Grid */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.summary-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1.25rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.summary-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.15);
}

.card-icon {
  font-size: 2.5rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border-radius: 12px;
}

.card-content {
  flex: 1;
}

.card-value {
  font-size: 2rem;
  font-weight: bold;
  color: #1f2937;
  line-height: 1;
}

.card-label {
  font-size: 0.9rem;
  color: #6b7280;
  margin-top: 0.5rem;
}

.card-hint {
  font-size: 0.75rem;
  color: #9ca3af;
  margin-top: 0.25rem;
  font-style: italic;
}

/* Charts Grid */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: 2rem;
}

/* Chart Cards */
.chart-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.chart-full-width {
  grid-column: 1 / -1;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #f3f4f6;
}

.chart-title {
  font-size: 1.25rem;
  font-weight: bold;
  color: #1f2937;
  margin: 0;
}

.chart-subtitle {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.chart-controls {
  display: flex;
  gap: 0.75rem;
}

.time-select {
  padding: 0.5rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  background-color: white;
  color: #374151;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.time-select:hover {
  border-color: #b91c1c;
}

.time-select:focus {
  outline: none;
  border-color: #b91c1c;
  box-shadow: 0 0 0 3px rgba(185, 28, 28, 0.1);
}

.chart-body {
  min-height: 280px;
  max-height: 320px;
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.chart-body canvas {
  max-height: 300px !important;
}

.chart-full-width .chart-body {
  min-height: 300px;
  max-height: 380px;
  height: 340px;
}

.chart-full-width .chart-body canvas {
  max-height: 340px !important;
}

.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  color: #9ca3af;
  padding: 3rem;
}

.no-data p {
  font-size: 1rem;
  font-weight: 500;
}

/* Table */
.table-container {
  overflow-x: auto;
  margin-top: 1rem;
}

.class-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.class-table thead {
  background-color: #f9fafb;
}

.class-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 2px solid #e5e7eb;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.class-table tbody tr {
  transition: background-color 0.2s ease;
}

.class-table tbody tr:hover {
  background-color: #f9fafb;
}

.class-table td {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
  color: #4b5563;
}

.class-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 500;
}

.class-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}

.text-bold {
  font-weight: 600;
  color: #1f2937;
  font-size: 1.1rem;
}

.progress-bar {
  width: 100%;
  height: 12px;
  background-color: #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  transition: width 0.5s ease;
  border-radius: 6px;
}

/* Harvest Estimation Tool */
.harvest-tool-card {
  border: 2px solid #b91c1c;
  background: linear-gradient(135deg, #fff 0%, #fef2f2 100%);
}

.harvest-tool-header {
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s ease;
}

.harvest-tool-header:hover {
  background-color: #fef2f2;
}

.toggle-btn {
  background: none;
  border: 2px solid #b91c1c;
  color: #b91c1c;
  font-size: 1rem;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: bold;
}

.toggle-btn:hover {
  background-color: #b91c1c;
  color: white;
}

.toggle-btn.expanded {
  background-color: #b91c1c;
  color: white;
}

.harvest-tool-content {
  padding: 1.5rem 0;
}



.harvest-slider {
  width: 100%;
  height: 8px;
  border-radius: 4px;
  background: linear-gradient(to right, #fee2e2 0%, #b91c1c 100%);
  outline: none;
  -webkit-appearance: none;
  appearance: none;
  cursor: pointer;
}

.harvest-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #b91c1c;
  border: 3px solid white;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  transition: all 0.2s ease;
}

.harvest-slider::-webkit-slider-thumb:hover {
  transform: scale(1.15);
  box-shadow: 0 4px 12px rgba(185, 28, 28, 0.4);
}

.harvest-slider::-moz-range-thumb {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #b91c1c;
  border: 3px solid white;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  transition: all 0.2s ease;
}

.harvest-slider::-moz-range-thumb:hover {
  transform: scale(1.15);
  box-shadow: 0 4px 12px rgba(185, 28, 28, 0.4);
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: #6b7280;
  margin-top: 0.25rem;
}



.harvest-info {
  padding: 1rem;
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  border-left: 4px solid #3b82f6;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
  color: #1e40af;
}

.harvest-timeline {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.timeline-item {
  background-color: white;
  border-radius: 12px;
  padding: 1.25rem;
  border: 2px solid #e5e7eb;
  transition: all 0.3s ease;
}

.timeline-item:hover {
  border-color: #b91c1c;
  box-shadow: 0 4px 12px rgba(185, 28, 28, 0.1);
}

.timeline-item.today {
  border-color: #b91c1c;
  background: linear-gradient(135deg, #fff 0%, #fef2f2 100%);
}

.timeline-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #f3f4f6;
}

.timeline-icon {
  font-size: 1.5rem;
}

.timeline-label {
  font-weight: 700;
  color: #1f2937;
  font-size: 1.1rem;
}

.timeline-content {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.harvest-result {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.75rem;
  background-color: #f9fafb;
  border-radius: 8px;
}

.harvest-result.primary {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border: 1px solid #fca5a5;
}

.harvest-result.secondary {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border: 1px solid #fbbf24;
}

.result-value {
  font-size: 1.75rem;
  font-weight: 800;
  color: #b91c1c;
}

.result-label {
  font-size: 0.95rem;
  font-weight: 600;
  color: #374151;
}

.result-count {
  font-size: 0.85rem;
  color: #6b7280;
  font-style: italic;
}

.harvest-total {
  margin-top: 1rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #b91c1c 0%, #991b1b 100%);
  border-radius: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
  box-shadow: 0 4px 12px rgba(185, 28, 28, 0.3);
}

.total-label {
  font-size: 1.1rem;
  font-weight: 600;
}

.total-value {
  font-size: 2.5rem;
  font-weight: 800;
}

.harvest-chart-container {
  margin-top: 1.5rem;
  padding: 1.5rem;
  background-color: white;
  border-radius: 12px;
  border: 2px solid #e5e7eb;
}

.harvest-chart-container .chart-subtitle {
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 1rem;
  text-align: center;
}

.harvest-chart-container canvas {
  height: 300px !important;
  max-height: 300px !important;
}

.harvest-disclaimer {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #fef3c7;
  border-left: 4px solid #f59e0b;
  border-radius: 8px;
  font-size: 0.9rem;
  color: #78350f;
  line-height: 1.6;
}

.harvest-empty {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
  font-size: 1.1rem;
}

/* Harvest Expand Animation */
.harvest-expand-enter-active,
.harvest-expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.harvest-expand-enter-from,
.harvest-expand-leave-to {
  max-height: 0;
  opacity: 0;
}

.harvest-expand-enter-to,
.harvest-expand-leave-from {
  max-height: 2000px;
  opacity: 1;
}

/* Responsive Design */
@media (max-width: 768px) {
  .modal-container {
    max-height: 95vh;
    border-radius: 16px;
  }

  .metrics-header-modal {
    padding: 1.5rem;
    flex-direction: column;
    gap: 1rem;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .modal-content-scroll {
    padding: 1.5rem;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }

  .chart-header {
    flex-direction: column;
    gap: 1rem;
  }

  .chart-controls {
    width: 100%;
    flex-direction: column;
  }

  .time-select {
    width: 100%;
  }

  .class-table {
    font-size: 0.875rem;
  }

  .class-table th,
  .class-table td {
    padding: 0.75rem 0.5rem;
  }

  .chart-body {
    min-height: 250px;
    max-height: 280px;
    height: 260px;
  }

  .chart-body canvas {
    max-height: 260px !important;
  }

  .chart-full-width .chart-body {
    min-height: 280px;
    max-height: 320px;
    height: 300px;
  }

  .chart-full-width .chart-body canvas {
    max-height: 300px !important;
  }
}

/* Utility Classes */
.text-4xl {
  font-size: 2.25rem;
}
</style>
