  /* Menu Section */
  const menuToggle = document.getElementById('menu-toggle');
const sidebar = document.getElementById('sidebar');

menuToggle.addEventListener('click', () => {
    const isActive = sidebar.classList.toggle('active');
    menuToggle.classList.toggle('active', isActive); // Toggle X effect
});

// Close sidebar when clicking outside
document.addEventListener('click', (event) => {
    const isClickInsideSidebar = sidebar.contains(event.target);
    const isClickInsideToggle = menuToggle.contains(event.target);

    if (!isClickInsideSidebar && !isClickInsideToggle && sidebar.classList.contains('active')) {
        sidebar.classList.remove('active');
        menuToggle.classList.remove('active'); // Reset icon to original state
    }
});
