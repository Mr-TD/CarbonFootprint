/**
 * Accessibility helpers for CarbonCredit.
 *
 * Handles:
 * - Auto-dismiss flash messages
 * - Keyboard navigation enhancements
 * - Focus management
 */

(function () {
    'use strict';

    // Auto-dismiss flash messages after 6 seconds
    var flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function (msg) {
        setTimeout(function () {
            msg.style.opacity = '0';
            msg.style.transform = 'translateX(30px)';
            msg.style.transition = 'opacity 0.3s, transform 0.3s';
            setTimeout(function () {
                if (msg.parentElement) {
                    msg.remove();
                }
            }, 300);
        }, 6000);
    });

    // Escape key closes flash messages
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            var flashes = document.querySelectorAll('.flash-message');
            flashes.forEach(function (msg) { msg.remove(); });

            // Close mobile nav if open
            var menu = document.getElementById('nav-menu');
            var toggle = document.getElementById('nav-toggle');
            if (menu && menu.classList.contains('nav-menu-open')) {
                menu.classList.remove('nav-menu-open');
                if (toggle) {
                    toggle.setAttribute('aria-expanded', 'false');
                    toggle.focus();
                }
            }
        }
    });

    // Ensure skip link target is focusable
    var mainContent = document.getElementById('main-content');
    if (mainContent && !mainContent.hasAttribute('tabindex')) {
        mainContent.setAttribute('tabindex', '-1');
    }

    // Announce dynamic content changes for screen readers
    window.announceToScreenReader = function (message) {
        var announcement = document.createElement('div');
        announcement.setAttribute('role', 'status');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.classList.add('sr-only');
        announcement.textContent = message;
        document.body.appendChild(announcement);
        setTimeout(function () {
            announcement.remove();
        }, 3000);
    };
})();
