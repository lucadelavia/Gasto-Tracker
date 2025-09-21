/**
 * Gasto Tracker - JavaScript Principal
 * Maneja la funcionalidad del dashboard de gastos
 */

// Variables globales
let estadisticas = [];
let chartInstance = null;

/**
 * Inicializa la aplicación cuando el DOM está listo
 */
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Función principal de inicialización
 */
function initializeApp() {
    setupFormEnhancements();
    setupFormSubmissionHandler();
    setupFilterEventListeners();
}

/**
 * Inicializa el gráfico de Chart.js con los datos proporcionados
 * @param {Array} data - Datos de estadísticas desde el backend
 */
function initializeChart(data) {
    estadisticas = data;
    const labels = estadisticas.filter(e => e.total > 0).map(e => e.categoria);
    const chartData = estadisticas.filter(e => e.total > 0).map(e => e.total);
    const colors = estadisticas.filter(e => e.total > 0).map(e => e.color);
    
    if (labels.length > 0) {
        const ctx = document.getElementById('graficoCategorias');
        if (ctx) {
            chartInstance = new Chart(ctx.getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: chartData,
                        backgroundColor: colors,
                        borderWidth: 2,
                        borderColor: '#fff',
                        hoverBorderWidth: 3,
                        hoverOffset: 10
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '70%',
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0,0,0,0.8)',
                            titleColor: '#fff',
                            bodyColor: '#fff',
                            borderColor: '#667eea',
                            borderWidth: 1,
                            callbacks: {
                                label: function(context) {
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((context.parsed / total) * 100).toFixed(1);
                                    return `${context.label}: $${context.parsed} (${percentage}%)`;
                                }
                            }
                        }
                    },
                    animation: {
                        animateRotate: true,
                        duration: 1500
                    }
                }
            });
        }
    }
}

/**
 * Configura mejoras visuales para los formularios
 */
function setupFormEnhancements() {
    const inputs = document.querySelectorAll('.form-control, .form-select');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });
}

/**
 * Maneja el estado de carga en el envío de formularios
 */
function setupFormSubmissionHandler() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="spinner-border spinner-border-sm me-2"></i>Guardando...';
                submitBtn.disabled = true;
                
                // Re-habilitar después de 3 segundos (en caso de error)
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 3000);
            }
        });
    });
}

/**
 * Configura los event listeners para los filtros
 */
function setupFilterEventListeners() {
    const fechaInicio = document.getElementById('fechaInicio');
    const fechaFin = document.getElementById('fechaFin');
    const filtroCategoria = document.getElementById('filtroCategoria');
    
    if (fechaInicio) fechaInicio.addEventListener('change', aplicarFiltros);
    if (fechaFin) fechaFin.addEventListener('change', aplicarFiltros);
    if (filtroCategoria) filtroCategoria.addEventListener('change', aplicarFiltros);
}

/**
 * Aplica los filtros a la tabla de gastos
 */
function aplicarFiltros() {
    const fechaInicio = document.getElementById('fechaInicio')?.value || '';
    const fechaFin = document.getElementById('fechaFin')?.value || '';
    const categoria = document.getElementById('filtroCategoria')?.value || '';
    
    // Convertir fechas de YYYY-MM-DD a DD-MM-YYYY para compatibilidad
    const fechaInicioFormatted = fechaInicio ? convertirFecha(fechaInicio) : '';
    const fechaFinFormatted = fechaFin ? convertirFecha(fechaFin) : '';
    
    // Filtrar tabla
    const filas = document.querySelectorAll('.gasto-row');
    let totalFiltrado = 0;
    let contadorVisible = 0;
    
    filas.forEach(fila => {
        const fechaGasto = fila.cells[4].textContent.trim();
        const categoriaGasto = fila.cells[1].querySelector('.badge')?.textContent.trim() || '';
        const montoTexto = fila.cells[3].textContent.trim().replace('$', '');
        const montoGasto = parseFloat(montoTexto) || 0;
        
        let mostrar = true;
        
        // Filtro por fecha inicio
        if (fechaInicioFormatted && !esFechaPosteriorOIgual(fechaGasto, fechaInicioFormatted)) {
            mostrar = false;
        }
        
        // Filtro por fecha fin
        if (fechaFinFormatted && !esFechaAnteriorOIgual(fechaGasto, fechaFinFormatted)) {
            mostrar = false;
        }
        
        // Filtro por categoría
        if (categoria && categoriaGasto !== categoria) {
            mostrar = false;
        }
        
        if (mostrar) {
            fila.style.display = '';
            totalFiltrado += montoGasto;
            contadorVisible++;
        } else {
            fila.style.display = 'none';
        }
    });
    
    // Actualizar total mostrado
    actualizarTotalFiltrado(totalFiltrado, contadorVisible);
}

/**
 * Limpia todos los filtros aplicados
 */
function limpiarFiltros() {
    const fechaInicio = document.getElementById('fechaInicio');
    const fechaFin = document.getElementById('fechaFin');
    const filtroCategoria = document.getElementById('filtroCategoria');
    
    if (fechaInicio) fechaInicio.value = '';
    if (fechaFin) fechaFin.value = '';
    if (filtroCategoria) filtroCategoria.value = '';
    
    // Mostrar todas las filas
    document.querySelectorAll('.gasto-row').forEach(fila => {
        fila.style.display = '';
    });
    
    // Restaurar total original
    location.reload();
}

/**
 * Convierte fecha de formato ISO (YYYY-MM-DD) a formato DD-MM-YYYY
 * @param {string} fechaISO - Fecha en formato ISO
 * @returns {string} Fecha en formato DD-MM-YYYY
 */
function convertirFecha(fechaISO) {
    const partes = fechaISO.split('-');
    return `${partes[2]}-${partes[1]}-${partes[0]}`;
}

/**
 * Verifica si fecha1 es posterior o igual a fecha2
 * @param {string} fecha1 - Fecha en formato DD-MM-YYYY
 * @param {string} fecha2 - Fecha en formato DD-MM-YYYY
 * @returns {boolean}
 */
function esFechaPosteriorOIgual(fecha1, fecha2) {
    const partes1 = fecha1.split('-');
    const partes2 = fecha2.split('-');
    const d1 = new Date(partes1[2], partes1[1] - 1, partes1[0]);
    const d2 = new Date(partes2[2], partes2[1] - 1, partes2[0]);
    return d1 >= d2;
}

/**
 * Verifica si fecha1 es anterior o igual a fecha2
 * @param {string} fecha1 - Fecha en formato DD-MM-YYYY
 * @param {string} fecha2 - Fecha en formato DD-MM-YYYY
 * @returns {boolean}
 */
function esFechaAnteriorOIgual(fecha1, fecha2) {
    const partes1 = fecha1.split('-');
    const partes2 = fecha2.split('-');
    const d1 = new Date(partes1[2], partes1[1] - 1, partes1[0]);
    const d2 = new Date(partes2[2], partes2[1] - 1, partes2[0]);
    return d1 <= d2;
}

/**
 * Actualiza el total mostrado en la tabla con los resultados filtrados
 * @param {number} total - Total calculado
 * @param {number} cantidad - Cantidad de registros
 */
function actualizarTotalFiltrado(total, cantidad) {
    const totalElement = document.querySelector('tfoot .text-success');
    if (totalElement) {
        totalElement.innerHTML = `$${total.toFixed(2)} (${cantidad} registros)`;
    }
}

/**
 * Abre el modal de edición con los datos del gasto seleccionado
 * @param {string} gastoId - ID del gasto a editar
 */
function editarGasto(gastoId) {
    const fila = document.querySelector(`tr[data-gasto-id="${gastoId}"]`);
    if (!fila) {
        console.error('No se encontró la fila del gasto:', gastoId);
        return;
    }
    
    // Extraer datos de la fila
    const descripcion = fila.getAttribute('data-descripcion') || '';
    const monto = fila.getAttribute('data-monto') || '';
    const categoria = fila.getAttribute('data-categoria') || '';
    const origen = fila.getAttribute('data-origen') || '';
    const fecha = fila.getAttribute('data-fecha') || '';
    
    // Llenar el formulario del modal
    const elementos = {
        'editGastoId': gastoId,
        'editDescripcion': descripcion,
        'editMonto': monto,
        'editCategoria': categoria,
        'editOrigen': origen,
        'editFecha': fecha
    };
    
    // Asignar valores a los campos del modal
    Object.entries(elementos).forEach(([id, valor]) => {
        const elemento = document.getElementById(id);
        if (elemento) {
            elemento.value = valor;
        } else {
            console.warn(`Elemento no encontrado: ${id}`);
        }
    });
    
    // Mostrar el modal
    const modalElement = document.getElementById('editarModal');
    if (modalElement && typeof bootstrap !== 'undefined') {
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
    } else {
        console.error('Modal o Bootstrap no encontrados');
    }
}

// Hacer funciones globales para compatibilidad con templates
window.aplicarFiltros = aplicarFiltros;
window.limpiarFiltros = limpiarFiltros;
window.editarGasto = editarGasto;
window.initializeChart = initializeChart;