/**
 * jQuery Raty - A Star Rating Plugin - http://wbotelhos.com/raty
 * --------------------------------------------------------------------------
 *
 * Licensed under The MIT License
 * 
 * @version     0.4
 * @since       11.06.2010
 * @author      Washington Botelho dos Santos
 * @link        http://wbotelhos.com/raty
 * @twitter     http://twitter.com/wbotelhos
 * @license     http://www.opensource.org/licenses/mit-license.php MIT 
 * @package     jQuery Plugins
 * 
 * Usage (default values):
 * --------------------------------------------------------------------------
  *	$('div#star').raty({
 *		hintList:    ['bad', 'poor', 'regular', 'good', 'gorgeous'],  // A hint information for default 5 stars.
 *		number:      5,                                               // Number of star.
 *		path:        'img,                                            // Path of images.
 *		readOnly:    false,                                           // read-only or not.
 *		scoreName:   'score',                                         // The name of target score.
 *      showHalf:    false,                                           // Active the half star.
 *      starHalf:    'star-half.png',                                 // The image of the half star.
 *		start:       0,                                               // Start with a score value.
 *		starOff:     'star-off.png',                                  // The image of the off star.
 *		starOn:      'star-on.png'                                    // The image of the on star.
 *      //onClick:   function() { alert('clicked!'); }                // A default function can to be setted here.
 *	});
 *  
 *	<div id="star"></div>
 *  
 * Public functions:
 * --------------------------------------------------------------------------
 *	$.fn.raty.start(3);                                                // Starting the rating with 3 stars later.
 *	$.fn.raty.readOnly(true);                                          // Adjusts the rating for read-only later.
 *	$.fn.raty.click(2);                                                // Click in a star later.
 *
 *	Should come after the current raty and before the anothers one. Because it takes the last called raty.
 *
 */

(function($) {

	// TODO: How to handle a particular container from a public function?

	$.fn.raty = function(settings) {
		options = $.extend({}, $.fn.raty.defaults, settings);

		if (this.attr('id') === undefined) {
			debug('Invalid selector!'); return;
		}

		$this = $(this);

		if (options.number > 20) {
			options.number = 20;
		}
	
		if (options.path.substring(options.path.length - 1, options.path.length) != '/') {
			options.path += '/';
		}
		
		// TODO: Using var for values that will be used into a function later (live/bind), to keep the current value and not the last one. Why, Mr. Anderson? Why? 
		var containerId = $this.attr('id');
		var path = options.path;
		var showHalf = options.showHalf;
		var starHalf = options.starHalf;
		var starOff = options.starOff;
		var starOn = options.starOn;
		var onClick = options.onClick;

		var start = 0;
		if (!isNaN(options.start) && options.start > 0) {
			start = (options.start > options.number) ? options.number : options.start;
		}

		var hint = '';
		for (var i = 1; i <= options.number; i++) {
			hint = (options.number <= options.hintList.length && options.hintList[i - 1] !== null) ? options.hintList[i - 1] : i;	// Avoids a nonexistent index (undefined) and ensures that the hint will be applied, it means different from null. Otherwise applies the current number.

			starFile = (start >= i) ? starOn : starOff;

			$this
			.append('<img id="' + containerId + '-' + i + '" src="' + path + starFile + '" alt="' + i + '" title="' + hint + '" class="' + containerId + '"/>');
                        //.append((i < options.number) ? '&nbsp;' : '');
		}

		$this
		.css('width', options.number * options.starWidth)																							// star: 16px and space 4px. A little bit more for safety Unbuntu's FF.
		.append('<input id="' + containerId + '-score" type="hidden" name="' + options.scoreName + '"/>');

		$('#' + containerId + '-score').val(start);

		if (showHalf) {
			var score = $('input#' + containerId + '-score').val();																	// [x ... x.25] || [x.26 ... x.75] || [x.76 ... (x + 1)]
			var rounded = Math.ceil(score);																							// (x + 1)
			var diff = (rounded - score).toFixed(1);																				// [0.9 ... 0.8] || [0.7 ... 0.3] || [0.2 ... 0]

			if (diff >= 0.3 && diff <= 0.7) {																						// 3.5			In the center interval the score is with a next star.
				rounded = rounded - 0.5;																							// 3 . half
				$('img#' + containerId + '-' + Math.ceil(rounded)).attr('src', path + starHalf);									// 				The next star is the half star.
			} else if (diff >= 0.8) {																								// 3			In the bottom interval the score is rounded down.
				rounded--;																											// 3 . --
			} else {																												// 4 . --		In the top interval the score is the same rounded top.
				$('img#' + containerId + '-' + rounded).attr('src', path + starOn);
			}
		}

		if (!options.readOnly) {

			$('img.' + containerId).live('mouseenter', function() {
				var qtyStar = $('img.' + containerId).length;

				for (var i = 1; i <= qtyStar; i++) {
					if (i <= this.alt) {
						$('img#' + containerId + '-' + i).attr('src', path + starOn);
					} else {
						$('img#' + containerId + '-' + i).attr('src', path + starOff);
					}
				}
			});
			
			$('img.' + containerId).live('click', function() {
				$('input#' + containerId + '-score').val(this.alt);

				if (onClick) { 
		          onClick(this.alt);
		        }
			});

			$this.live('mouseleave', function() {
				var id = $(this).attr('id');
				var qtyStar = $('img.' + id).length;
				var score = $('input#' + id + '-score').val();

				for (var i = 1; i <= qtyStar; i++) {
					if (i <= score) {
						$('img#' + id + '-' + i).attr('src', path + starOn);
					} else {
						$('img#' + id + '-' + i).attr('src', path + starOff);
					}
				}

				if (showHalf) {
					var score = $('input#' + id + '-score').val();
					var rounded = Math.ceil(score);
					var diff = (rounded - score).toFixed(1);

					if (diff >= 0.3 && diff <= 0.7) {
						rounded = rounded - 0.5;
						$('img#' + id + '-' + Math.ceil(rounded)).attr('src', path + starHalf);
					} else if (diff >= 0.8) {
						rounded--;
					} else {
						$('img#' + id + '-' + rounded).attr('src', path + starOn);
					}
				}
			}).css('cursor', 'pointer');
		} else {
			$this.css('cursor', 'default');
		}

		return $this;
	};
	
	$.fn.raty.defaults = {
		hintList:		['bad', 'poor', 'regular', 'good', 'gorgeous'],
		number:			5,
		path:			'img/',
		readOnly:		false,
		scoreName:		'score',
		showHalf:		false,
		starHalf:		'star-half.png',
		start:			0,
		starOff:		'star-off.png',
		starOn:			'star-on.png',
                starWidth:              17
		//onClick:		function() { alert('clicked!'); }
	};

	$.fn.raty.readOnly = function(boo) {
		if (boo) {
			$('img.' + $this.attr('id')).die();
			$this.css('cursor', 'default').die();
		} else { 
			liveEnter();
			liveLeave();
			liveClick();
			$this.css('cursor', 'pointer');
		}
		return $.fn.raty;
	};

	$.fn.raty.start = function(start) {
		initialize(start);
		return $.fn.raty;
	};

	$.fn.raty.click = function(score) {
		var star = (score >= options.number) ? options.number : score;
		initialize(star);
		if (options.onClick) {
			options.onClick(star);
		} else {
			debug('You should add the "onClick: function() {}" option.');
		}
		return $.fn.raty;
	};
	
	// TODO: Repeated on purpose for now! Because options.x here works as current value, unlike in the function body. Why, Mr. Anderson? Why?
	function liveEnter() {
		var id = $this.attr('id');
		$('img.' + id).live('mouseenter', function() {
			var qtyStar = $('img.' + id).length;

			for (var i = 1; i <= qtyStar; i++) {
				if (i <= this.alt) {
					$('img#' + id + '-' + i).attr('src', options.path + options.starOn);
				} else {
					$('img#' + id + '-' + i).attr('src', options.path + options.starOff);
				}
			}
		});
	};
	
	function liveLeave() {
		$this.live('mouseleave', function() { 
			var id  = $(this).attr('id');
			var qtyStar = $('img.' + id).length;
			var score = $('input#' + id + '-score').val();

			for (var i = 1; i <= qtyStar; i++) {
				if (i <= score) {
					$('img#' + id + '-' + i).attr('src', options.path + options.starOn);
				} else {
					$('img#' + id + '-' + i).attr('src', options.path + options.starOff);
				}
			}
		});
	};

	function liveClick() {
		var id = $this.attr('id');
		$('img.' + id).live('click', function() {
			$('input#' + id + '-score').val(this.alt);
		});
	};

	function initialize(start) {
		var id = $this.attr('id');
		var qtyStar = $('img.' + id).length;
		$('input#' + id + '-score').val(start);

		for (var i = 1; i <= qtyStar; i++) {
			if (i <= start) {
				$('img#' + id + '-' + i).attr('src', options.path + options.starOn);
			} else {
				$('img#' + id + '-' + i).attr('src', options.path + options.starOff);
			}
		}
	};
	
	function debug(message) {
		if (window.console && window.console.log) {
			window.console.log(message);
		}
	};

})(jQuery);