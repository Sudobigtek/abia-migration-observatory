// Abia Observatory — Offline Form Queue
(function() {
  var db = null;

  function initDB() {
    return new Promise(function(resolve, reject) {
      var request = indexedDB.open('AbiaObservatoryDB', 1);
      request.onupgradeneeded = function(e) {
        var db = e.target.result;
        if (!db.objectStoreNames.contains('formQueue')) {
          db.createObjectStore('formQueue', { keyPath: 'id', autoIncrement: true });
        }
      };
      request.onsuccess = function(e) { db = e.target.result; resolve(db); };
      request.onerror = function(e) { reject(e.target.error); };
    });
  }

  function queueForm(formElement) {
    var formData = new FormData(formElement);
    var body = new URLSearchParams(formData).toString();
    var url = formElement.action || window.location.href;

    var tx = db.transaction('formQueue', 'readwrite');
    var store = tx.objectStore('formQueue');
    store.add({ url: url, body: body, createdAt: Date.now() });

    showToast('Form saved offline. Will sync when connection returns.', 'warning');

    if ('serviceWorker' in navigator && 'SyncManager' in window) {
      navigator.serviceWorker.ready.then(function(reg) {
        reg.sync.register('sync-forms');
      });
    }
  }

  function syncNow() {
    if (!navigator.onLine) {
      showToast('You are offline. Forms will sync automatically when online.', 'info');
      return;
    }
    var tx = db.transaction('formQueue', 'readonly');
    var store = tx.objectStore('formQueue');
    store.getAll().onsuccess = function(e) {
      var forms = e.target.result;
      var synced = 0;
      forms.forEach(function(form) {
        fetch(form.url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: form.body
        }).then(function(response) {
          if (response.ok) {
            var delTx = db.transaction('formQueue', 'readwrite');
            delTx.objectStore('formQueue').delete(form.id);
            synced++;
          }
        }).catch(function(err) { console.error('Sync error:', err); });
      });
      setTimeout(function() {
        if (synced > 0) {
          showToast(synced + ' form(s) synced successfully!', 'success');
          setTimeout(function() { location.reload(); }, 1500);
        } else {
          showToast('No pending forms to sync.', 'info');
        }
      }, 1000);
    };
  }

  function showToast(message, type) {
    var colors = { success: '#198754', warning: '#ffc107', info: '#0dcaf0', danger: '#dc3545' };
    var toast = document.createElement('div');
    var bg = colors[type] || colors.info;
    var fg = (type === 'warning') ? '#000' : '#fff';
    toast.style.cssText = 'position:fixed;top:20px;right:20px;z-index:9999;padding:1rem 1.5rem;border-radius:8px;background:' + bg + ';color:' + fg + ';box-shadow:0 4px 12px rgba(0,0,0,0.15);font-weight:500;';
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(function() { toast.remove(); }, 4000);
  }

  function setupOfflineForms() {
    document.querySelectorAll('form[method="post"]').forEach(function(form) {
      form.addEventListener('submit', function(e) {
        if (!navigator.onLine) {
          e.preventDefault();
          queueForm(form);
        }
      });
    });
    var nav = document.querySelector('.sidebar .nav');
    if (nav && !document.getElementById('sync-btn')) {
      var syncLink = document.createElement('a');
      syncLink.id = 'sync-btn';
      syncLink.className = 'nav-link';
      syncLink.href = '#';
      syncLink.innerHTML = '<i class="bi bi-cloud-arrow-up"></i> Sync Now';
      syncLink.onclick = function(e) { e.preventDefault(); syncNow(); };
      nav.appendChild(syncLink);
    }
  }

  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
      navigator.serviceWorker.register('/static/service-worker.js')
        .then(function(reg) { console.log('SW registered:', reg.scope); })
        .catch(function(err) { console.log('SW failed:', err); });
    });
  }

  window.addEventListener('online', function() {
    showToast('Back online! Syncing queued forms...', 'success');
    syncNow();
  });

  window.addEventListener('offline', function() {
    showToast('You are offline. Forms will be saved locally.', 'warning');
  });

  document.addEventListener('DOMContentLoaded', function() {
    initDB().then(function() { setupOfflineForms(); }).catch(function(e) { console.error(e); });
  });
})();
