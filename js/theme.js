// Run the callback once the DOM is ready, in the order that callbacks are registered.
function onReady (callback) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', callback);
    } else {
        callback();
    }
}

function toggleClass (selector, className) {
    document.querySelectorAll(selector).forEach(function (element) {
        element.classList.toggle(className);
    });
}

function removeClass (elements, className) {
    elements.forEach(function (element) {
        element.classList.remove(className);
    });
}

function siblings (element) {
    return Array.prototype.filter.call(element.parentNode.children, function (sibling) {
        return sibling !== element;
    });
}

// Sphinx theme nav state
function ThemeNav () {

    var nav = {
        navBar: null,
        winScroll: false,
        winResize: false,
        linkScroll: false,
        winPosition: 0,
        winHeight: null,
        docHeight: null,
        isRunning: false
    };

    nav.enable = function () {
        var self = this;

        if (!self.isRunning) {
            self.isRunning = true;
            onReady(function () {
                // Set scroll monitor
                window.addEventListener('scroll', function () {
                    if (!self.linkScroll) {
                        self.winScroll = true;
                    }
                });
                setInterval(function () { if (self.winScroll) self.onScroll(); }, 25);

                // Set resize monitor
                window.addEventListener('resize', function () {
                    self.winResize = true;
                });
                setInterval(function () { if (self.winResize) self.onResize(); }, 25);
                self.onResize();
            });
        };
    };

    nav.init = function () {
        var self = this;

        this.navBar = document.querySelector('div.wy-side-scroll');

        // Set up javascript UX bits
        document.addEventListener('click', function (event) {
            var target = event.target;

            // Shift nav in mobile when clicking the menu.
            if (target.closest("[data-toggle='wy-nav-top']")) {
                toggleClass("[data-toggle='wy-nav-shift']", 'shift');
                toggleClass("[data-toggle='rst-versions']", 'shift');
            }

            // Nav menu link click operations
            var link = target.closest('.wy-menu-vertical .current ul li a');
            if (link) {
                // Close menu when you click a link.
                removeClass(document.querySelectorAll("[data-toggle='wy-nav-shift']"), 'shift');
                toggleClass("[data-toggle='rst-versions']", 'shift');
                // Handle dynamic display of l3 and l4 nav lists
                self.toggleCurrent(link);
                self.hashChange();
            }

            if (target.closest("[data-toggle='rst-current-version']")) {
                toggleClass("[data-toggle='rst-versions']", 'shift-up');
            }
        });

        // Make tables responsive
        document.querySelectorAll('table.docutils:not(.field-list)').forEach(function (table) {
            var wrapper = document.createElement('div');
            wrapper.className = 'wy-table-responsive';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        });

        // Add expand links to all parents of nested ul
        var links = new Set();
        document.querySelectorAll('.wy-menu-vertical ul:not(.simple)').forEach(function (ul) {
            siblings(ul).forEach(function (sibling) {
                if (sibling.tagName === 'A') {
                    links.add(sibling);
                }
            });
        });
        links.forEach(function (link) {
            var expand = document.createElement('span');
            expand.className = 'toctree-expand';
            expand.addEventListener('click', function (event) {
                self.toggleCurrent(link);
                event.stopPropagation();
                event.preventDefault();
            });
            link.prepend(expand);
        });

        this.reset();
        window.addEventListener('hashchange', this.reset);
    };

    nav.reset = function () {
        // Get anchor from URL and open up nested nav
        var anchor = encodeURI(window.location.hash);
        if (anchor) {
            try {
                var links = document.querySelectorAll('.wy-menu-vertical [href="' + anchor + '"]');
                removeClass(document.querySelectorAll('.wy-menu-vertical li.toctree-l1 li.current'), 'current');
                links.forEach(function (link) {
                    ['toctree-l2', 'toctree-l3', 'toctree-l4', 'toctree-l5'].forEach(function (level) {
                        var item = link.closest('li.' + level);
                        if (item) {
                            item.classList.add('current');
                        }
                    });
                });
            }
            catch (err) {
                console.log("Error expanding nav for anchor", err);
            }
        }
    };

    nav.onScroll = function () {
        this.winScroll = false;
        var newWinPosition = window.scrollY,
            winBottom = newWinPosition + this.winHeight,
            navPosition = this.navBar.scrollTop,
            newNavPosition = navPosition + (newWinPosition - this.winPosition);
        if (newWinPosition < 0 || winBottom > this.docHeight) {
            return;
        }
        this.navBar.scrollTop = newNavPosition;
        this.winPosition = newWinPosition;
    };

    nav.onResize = function () {
        this.winResize = false;
        this.winHeight = document.documentElement.clientHeight;
        this.docHeight = document.documentElement.scrollHeight;
    };

    nav.hashChange = function () {
        var self = this;
        this.linkScroll = true;
        window.addEventListener('hashchange', function () {
            self.linkScroll = false;
        }, { once: true });
    };

    nav.toggleCurrent = function (elem) {
        var parent_li = elem.closest('li');
        siblings(parent_li).forEach(function (sibling) {
            if (sibling.matches('li.current')) {
                sibling.classList.remove('current');
            }
            removeClass(sibling.querySelectorAll('li.current'), 'current');
        });
        removeClass(parent_li.querySelectorAll(':scope > ul li.current'), 'current');
        parent_li.classList.toggle('current');
    }

    return nav;
};

module.exports.ThemeNav = ThemeNav();

if (typeof(window) != 'undefined') {
    window.SphinxRtdTheme = { StickyNav: module.exports.ThemeNav };

    // Run before StickyNav.enable(), which the layout calls on ready after this script, as enable() uses init()'s state.
    onReady(function () {
        module.exports.ThemeNav.init();
    });
}
