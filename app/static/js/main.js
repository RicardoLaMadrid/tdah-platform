// Main JavaScript para Plataforma TDAH

// Animación de entrada para elementos
document.addEventListener('DOMContentLoaded', function() {
    // Agregar clase fade-in a cards
    const cards = document.querySelectorAll('.card, .stat-card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in');
        }, index * 100);
    });
    
    // Auto-hide alerts después de 5 segundos
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Utilidades para hacer peticiones AJAX
const api = {
    async get(url) {
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error('Error en la petición');
            return await response.json();
        } catch (error) {
            console.error('Error:', error);
            showNotification('Error al cargar los datos', 'danger');
            return null;
        }
    },
    
    async post(url, data) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error('Error en la petición');
            return await response.json();
        } catch (error) {
            console.error('Error:', error);
            showNotification('Error al guardar los datos', 'danger');
            return null;
        }
    }
};

// Mostrar notificaciones
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container-fluid') || document.body;
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alertDiv);
        bsAlert.close();
    }, 5000);
}

// Confirmar acciones destructivas
function confirmAction(message = '¿Estás seguro?') {
    return confirm(message);
}

// Formatear tiempo (segundos a mm:ss)
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// Formatear fecha
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Calcular color según puntuación
function getScoreColor(score) {
    if (score >= 80) return 'success';
    if (score >= 60) return 'info';
    if (score >= 40) return 'warning';
    return 'danger';
}

// Crear gráfico de progreso (usando Chart.js si está disponible)
function createProgressChart(canvasId, labels, data) {
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js no está cargado');
        return;
    }
    
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Puntuación de Atención',
                data: data,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

// Manejo de carga de archivos
class FileUploader {
    constructor(inputId, options = {}) {
        this.input = document.getElementById(inputId);
        this.maxSize = options.maxSize || 50 * 1024 * 1024; // 50MB
        this.allowedTypes = options.allowedTypes || ['video/*', 'audio/*'];
        
        if (this.input) {
            this.input.addEventListener('change', (e) => this.handleFile(e));
        }
    }
    
    handleFile(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        // Validar tamaño
        if (file.size > this.maxSize) {
            showNotification('El archivo es demasiado grande', 'danger');
            this.input.value = '';
            return;
        }
        
        // Validar tipo
        const fileType = file.type;
        const isAllowed = this.allowedTypes.some(type => {
            if (type.endsWith('/*')) {
                return fileType.startsWith(type.replace('/*', ''));
            }
            return fileType === type;
        });
        
        if (!isAllowed) {
            showNotification('Tipo de archivo no permitido', 'danger');
            this.input.value = '';
            return;
        }
        
        showNotification('Archivo cargado correctamente', 'success');
    }
}

// Temporizador de actividad
class ActivityTimer {
    constructor() {
        this.startTime = null;
        this.elapsed = 0;
        this.interval = null;
    }
    
    start() {
        this.startTime = Date.now();
        this.interval = setInterval(() => {
            this.elapsed = Math.floor((Date.now() - this.startTime) / 1000);
            this.updateDisplay();
        }, 1000);
    }
    
    stop() {
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }
        return this.elapsed;
    }
    
    updateDisplay() {
        const display = document.getElementById('timer-display');
        if (display) {
            display.textContent = formatTime(this.elapsed);
        }
    }
}

// Captura de video/audio
class MediaRecorder {
    constructor() {
        this.stream = null;
        this.recorder = null;
        this.chunks = [];
    }
    
    async startCamera() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: true
            });
            
            const videoElement = document.getElementById('camera-preview');
            if (videoElement) {
                videoElement.srcObject = this.stream;
            }
            
            return true;
        } catch (error) {
            console.error('Error al acceder a la cámara:', error);
            showNotification('No se pudo acceder a la cámara', 'danger');
            return false;
        }
    }
    
    startRecording() {
        if (!this.stream) {
            showNotification('Primero debes iniciar la cámara', 'warning');
            return;
        }
        
        this.chunks = [];
        this.recorder = new window.MediaRecorder(this.stream);
        
        this.recorder.ondataavailable = (e) => {
            if (e.data.size > 0) {
                this.chunks.push(e.data);
            }
        };
        
        this.recorder.start();
        showNotification('Grabación iniciada', 'info');
    }
    
    stopRecording() {
        return new Promise((resolve) => {
            if (!this.recorder) {
                resolve(null);
                return;
            }
            
            this.recorder.onstop = () => {
                const blob = new Blob(this.chunks, { type: 'video/webm' });
                resolve(blob);
            };
            
            this.recorder.stop();
            showNotification('Grabación detenida', 'success');
        });
    }
    
    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
    }
}

// Inicializar componentes globales
window.api = api;
window.showNotification = showNotification;
window.confirmAction = confirmAction;
window.formatTime = formatTime;
window.formatDate = formatDate;
window.getScoreColor = getScoreColor;
window.createProgressChart = createProgressChart;
window.FileUploader = FileUploader;
window.ActivityTimer = ActivityTimer;
window.MediaRecorder = MediaRecorder;