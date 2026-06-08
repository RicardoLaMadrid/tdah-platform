// Utilidades compartidas: activity player y actividades AR

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

function showNotification(message, type = 'info') {
  const palette = {
    info:    'bg-blue-500',
    success: 'bg-emerald-500',
    warning: 'bg-amber-500',
    danger:  'bg-red-500',
  };
  const bg = palette[type] || palette.info;
  const toast = document.createElement('div');
  toast.className = `fixed top-4 right-4 z-[9999] px-4 py-3 rounded-xl text-white text-sm font-semibold shadow-lg ${bg}`;
  toast.style.transition = 'opacity 0.3s';
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

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
      this._updateDisplay();
    }, 1000);
  }

  stop() {
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = null;
    }
    return this.elapsed;
  }

  _updateDisplay() {
    const el = document.getElementById('timer-display');
    if (el) el.textContent = formatTime(this.elapsed);
  }
}

window.formatTime = formatTime;
window.showNotification = showNotification;
window.ActivityTimer = ActivityTimer;
