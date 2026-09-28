/**
 * Customer Feedback Dashboard - Reports Module Controller
 */

document.addEventListener('DOMContentLoaded', function () {
  const printBtn = document.getElementById('printReportBtn');
  if (printBtn) {
    printBtn.addEventListener('click', function () {
      window.print();
    });
  }
});
