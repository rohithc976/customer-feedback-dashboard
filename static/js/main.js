/**
 * Customer Feedback Dashboard - Main Application Script
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Mobile Sidebar Toggle
  const sidebar = document.querySelector('.app-sidebar');
  const toggleBtn = document.querySelector('.sidebar-toggle-btn');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', function () {
      sidebar.classList.toggle('open');
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function (e) {
      if (window.innerWidth <= 768 && sidebar.classList.contains('open')) {
        if (!sidebar.contains(e.target) && !toggleBtn.contains(e.target)) {
          sidebar.classList.remove('open');
        }
      }
    });
  }

  // 2. Alert Dismissal with Smooth Fade
  const alertCloseButtons = document.querySelectorAll('.alert-close');
  alertCloseButtons.forEach(function (button) {
    button.addEventListener('click', function () {
      const alert = this.closest('.alert');
      if (alert) {
        alert.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-10px)';
        setTimeout(() => alert.remove(), 300);
      }
    });
  });

  // Auto-dismiss success alerts after 6 seconds
  const autoAlerts = document.querySelectorAll('.alert-success, .alert-info');
  autoAlerts.forEach(function (alert) {
    setTimeout(function () {
      if (alert && alert.parentNode) {
        alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-8px)';
        setTimeout(() => alert.remove(), 400);
      }
    }, 6000);
  });

  // 3. Delete Confirmation Modal
  window.openDeleteModal = function (feedbackId, customerName) {
    const modal = document.getElementById('deleteConfirmModal');
    const form = document.getElementById('deleteConfirmForm');
    const nameSpan = document.getElementById('deleteTargetName');

    if (modal && form) {
      form.action = `/feedback/${feedbackId}/delete`;
      if (nameSpan) {
        nameSpan.textContent = customerName ? `'${customerName}'` : `Feedback #${feedbackId}`;
      }
      modal.classList.add('show');
    }
  };

  window.closeDeleteModal = function () {
    const modal = document.getElementById('deleteConfirmModal');
    if (modal) {
      modal.classList.remove('show');
    }
  };

  // Close modal when clicking backdrop
  const deleteModal = document.getElementById('deleteConfirmModal');
  if (deleteModal) {
    deleteModal.addEventListener('click', function (e) {
      if (e.target === deleteModal) {
        closeDeleteModal();
      }
    });
  }
});
