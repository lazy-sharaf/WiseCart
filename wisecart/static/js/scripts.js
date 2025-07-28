// Enhanced Burger Menu with Animated Icon and Smooth Interactions
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const burgerMenu = document.getElementById('burger-menu');
    const closeSidebarBtn = document.getElementById('close-sidebar');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const burgerLines = document.querySelectorAll('.burger-line-1, .burger-line-2, .burger-line-3');
    const desktopNav = document.getElementById('desktop-nav');

    // Burger Icon Animation Classes
    const burgerAnimations = {
        line1: 'rotate-45 translate-y-2',
        line2: 'opacity-0',
        line3: '-rotate-45 -translate-y-2'
    };

    // Open Sidebar with Enhanced Animation
    burgerMenu.addEventListener('click', function() {
        // Animate burger icon
        burgerLines[0].classList.add(...burgerAnimations.line1.split(' '));
        burgerLines[1].classList.add(burgerAnimations.line2);
        burgerLines[2].classList.add(...burgerAnimations.line3.split(' '));

        // Show sidebar with enhanced animation
        sidebar.classList.remove('-translate-x-full');
        sidebar.classList.add('translate-x-0');
        
        // Show overlay with backdrop blur
        sidebarOverlay.classList.remove('opacity-0', 'pointer-events-none');
        sidebarOverlay.classList.add('opacity-100', 'pointer-events-auto');

        // Hide desktop navigation when sidebar is open
        if (desktopNav) {
            desktopNav.style.display = 'none';
        }

        // Add body scroll lock
        document.body.style.overflow = 'hidden';

        // Add entrance animation to sidebar items
        const sidebarItems = sidebar.querySelectorAll('nav a, nav div');
        sidebarItems.forEach((item, index) => {
            item.style.opacity = '0';
            item.style.transform = 'translateX(-20px)';
            
            setTimeout(() => {
                item.style.transition = 'all 0.3s ease-out';
                item.style.opacity = '1';
                item.style.transform = 'translateX(0)';
            }, 100 + (index * 50));
        });
    });

    // Close Sidebar Function with Enhanced Animation
    function closeSidebar() {
        // Reset burger icon
        burgerLines[0].classList.remove(...burgerAnimations.line1.split(' '));
        burgerLines[1].classList.remove(burgerAnimations.line2);
        burgerLines[2].classList.remove(...burgerAnimations.line3.split(' '));

        // Hide sidebar
        sidebar.classList.remove('translate-x-0');
        sidebar.classList.add('-translate-x-full');
        
        // Hide overlay
        sidebarOverlay.classList.remove('opacity-100', 'pointer-events-auto');
        sidebarOverlay.classList.add('opacity-0', 'pointer-events-none');

        // Show desktop navigation when sidebar is closed
        if (desktopNav) {
            desktopNav.style.display = 'flex';
        }

        // Restore body scroll
        document.body.style.overflow = '';

        // Reset sidebar items animation
        const sidebarItems = sidebar.querySelectorAll('nav a, nav div');
        sidebarItems.forEach(item => {
            item.style.opacity = '';
            item.style.transform = '';
            item.style.transition = '';
        });
    }

    // Close button event
    closeSidebarBtn.addEventListener('click', closeSidebar);

    // Close when clicking overlay
    sidebarOverlay.addEventListener('click', closeSidebar);

    // Enhanced click outside detection
    document.addEventListener('click', function(event) {
        const isClickInsideSidebar = sidebar.contains(event.target);
        const isClickOnBurgerMenu = burgerMenu.contains(event.target);

        if (!isClickInsideSidebar && !isClickOnBurgerMenu && 
            !sidebar.classList.contains('-translate-x-full')) {
            closeSidebar();
        }
    });

    // Keyboard support (ESC key)
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && !sidebar.classList.contains('-translate-x-full')) {
            closeSidebar();
        }
    });

    // Enhanced hover effects for sidebar items
    const sidebarLinks = sidebar.querySelectorAll('nav a');
    sidebarLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.transform = 'translateX(8px) scale(1.02)';
        });

        link.addEventListener('mouseleave', function() {
            this.style.transform = 'translateX(0) scale(1)';
        });
    });

    // Smooth scroll for anchor links
    sidebarLinks.forEach(link => {
        if (link.getAttribute('href').startsWith('#')) {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = this.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                
                if (targetElement) {
                    closeSidebar();
                    setTimeout(() => {
                        targetElement.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }, 300);
                }
            });
        }
    });

    // Add ripple effect to burger button
    burgerMenu.addEventListener('click', function(e) {
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple');
        
        this.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    });

    // Add CSS for ripple effect
    const style = document.createElement('style');
    style.textContent = `
        .ripple {
            position: absolute;
            border-radius: 50%;
            background: rgba(59, 130, 246, 0.3);
            transform: scale(0);
            animation: ripple-animation 0.6s linear;
            pointer-events: none;
        }
        
        @keyframes ripple-animation {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        #burger-menu {
            position: relative;
            overflow: hidden;
        }
        
        .burger-line-1, .burger-line-2, .burger-line-3 {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        #sidebar nav a {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        #sidebar nav a:hover {
            transform: translateX(8px) scale(1.02);
        }
    `;
    document.head.appendChild(style);
});