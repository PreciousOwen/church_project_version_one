// Reserved for landing-page interactions.

document.addEventListener('DOMContentLoaded', function () {
	var sliders = Array.prototype.slice.call(document.querySelectorAll('[data-hero-slider]'));

	if (sliders.length === 0) {
		return;
	}

	sliders.forEach(function (slider) {
		var scroll = slider.querySelector('.hero-scroll');
		var prevButton = slider.querySelector('.hero-nav-prev');
		var nextButton = slider.querySelector('.hero-nav-next');

		if (!scroll || !prevButton || !nextButton) {
			return;
		}

		var slides = Array.prototype.slice.call(scroll.querySelectorAll('img'));
		if (slides.length < 2) {
			prevButton.disabled = true;
			nextButton.disabled = true;
			return;
		}

		var index = 0;

		function scrollToIndex(nextIndex) {
			var slideWidth = scroll.clientWidth;
			if (!slideWidth) {
				return;
			}

			index = (nextIndex + slides.length) % slides.length;
			scroll.scrollTo({
				left: slideWidth * index,
				behavior: 'smooth'
			});
		}

		nextButton.addEventListener('click', function () {
			scrollToIndex(index + 1);
		});

		prevButton.addEventListener('click', function () {
			scrollToIndex(index - 1);
		});
	});
});

document.addEventListener('DOMContentLoaded', function () {
	var grids = Array.prototype.slice.call(document.querySelectorAll('.upcoming-events-grid'));
	if (grids.length === 0) {
		return;
	}

	var updateGrid = function (grid) {
		var cards = grid.querySelectorAll('.upcoming-event-card');
		var count = cards.length;
		if (count === 0) {
			grid.classList.remove('is-scrollable');
			return;
		}

		var isMobile = window.matchMedia('(max-width: 767.98px)').matches;
		var threshold = isMobile ? 2 : 3;
		if (count > threshold) {
			grid.classList.add('is-scrollable');
		} else {
			grid.classList.remove('is-scrollable');
		}
	};

	var refreshAll = function () {
		grids.forEach(updateGrid);
	};

	refreshAll();
	window.addEventListener('resize', refreshAll);
});

document.addEventListener('DOMContentLoaded', function () {
	var collapse = document.getElementById('navbarMain');
	var backdrop = document.querySelector('[data-navbar-backdrop]');
	var closeButton = collapse ? collapse.querySelector('.navbar-close') : null;
	var toggleButton = document.querySelector('.navbar-toggler');

	if (!collapse || !backdrop) {
		return;
	}

	var showBackdrop = function () {
		backdrop.classList.add('is-visible');
	};
	var hideBackdrop = function () {
		backdrop.classList.remove('is-visible');
	};
	var hideCollapse = function () {
		if (window.jQuery && window.jQuery.fn && window.jQuery.fn.collapse) {
			window.jQuery(collapse).collapse('hide');
		} else {
			collapse.classList.remove('show');
		}
	};

	if (window.jQuery && window.jQuery.fn && window.jQuery.fn.collapse) {
		window.jQuery(collapse).on('shown.bs.collapse', showBackdrop);
		window.jQuery(collapse).on('hidden.bs.collapse', hideBackdrop);
	} else if (toggleButton) {
		toggleButton.addEventListener('click', function () {
			window.setTimeout(function () {
				if (collapse.classList.contains('show')) {
					showBackdrop();
				} else {
					hideBackdrop();
				}
			}, 10);
		});
	}

	if (closeButton) {
		closeButton.addEventListener('click', hideCollapse);
	}

	backdrop.addEventListener('click', hideCollapse);
});

document.addEventListener('DOMContentLoaded', function () {
	var pageLoader = document.getElementById('pageLoader');
	var loaderKey = 'pageLoaderStart';
	var showPageLoader = function () {
		if (pageLoader) {
			pageLoader.classList.add('is-visible');
		}
	};
	var hidePageLoader = function () {
		if (pageLoader) {
			pageLoader.classList.remove('is-visible');
		}
	};
	var initPageLoader = function () {
		if (!pageLoader) {
			return;
		}
		showPageLoader();

		window.addEventListener('load', function () {
			hidePageLoader();
			window.sessionStorage.removeItem(loaderKey);
		});

		window.addEventListener('pageshow', function () {
			hidePageLoader();
			window.sessionStorage.removeItem(loaderKey);
		});
	};

	document.addEventListener('click', function (event) {
		var target = event.target;
		if (!(target instanceof HTMLElement)) {
			return;
		}

		var link = target.closest('a');
		if (!link) {
			return;
		}

		var href = link.getAttribute('href');
		if (!href || href.indexOf('#') === 0 || href.indexOf('javascript:') === 0 || href.indexOf('mailto:') === 0 || href.indexOf('tel:') === 0) {
			return;
		}

		if (link.getAttribute('target') === '_blank' || link.hasAttribute('download')) {
			return;
		}

		showPageLoader();
		window.sessionStorage.setItem(loaderKey, String(Date.now()));
	});

	document.addEventListener('submit', function (event) {
		var form = event.target;
		if (form && form.tagName === 'FORM') {
			showPageLoader();
			window.sessionStorage.setItem(loaderKey, String(Date.now()));
		}
	}, true);

		window.addEventListener('beforeunload', function () {
			showPageLoader();
		window.sessionStorage.setItem(loaderKey, String(Date.now()));
		});

		initPageLoader();
});
