           // Wait for the DOM to be fully loaded
           document.addEventListener('DOMContentLoaded', function() {
            // DOM Elements
            var burgerMenu = document.getElementById('burger-menu');
            var closeSidebarBtn = document.getElementById('close-sidebar');
            var sidebar = document.getElementById('sidebar');
            var sidebarOverlay = document.getElementById('sidebar-overlay');

            // Open Sidebar
            burgerMenu.addEventListener('click', function() {
                sidebar.classList.remove('-translate-x-full');
                sidebarOverlay.classList.remove('opacity-0');
                sidebarOverlay.classList.add('opacity-20');
            });

            // Close Sidebar Function
            function closeSidebar() {
                sidebar.classList.add('-translate-x-full');
                sidebarOverlay.classList.remove('opacity-20');
                sidebarOverlay.classList.add('opacity-0');
            }

            // Close button event
            closeSidebarBtn.addEventListener('click', closeSidebar);

            // Close when clicking outside sidebar
            sidebarOverlay.addEventListener('click', closeSidebar);

            // Close sidebar when clicking outside
            document.addEventListener('click', function(event) {
                var isClickInsideSidebar = sidebar.contains(event.target);
                var isClickOnBurgerMenu = burgerMenu.contains(event.target);

                if (!isClickInsideSidebar && !isClickOnBurgerMenu && 
                    !sidebar.classList.contains('-translate-x-full')) {
                    closeSidebar();
                }
            });
        });