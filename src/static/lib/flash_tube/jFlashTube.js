/*
 * jFlashTube
 * 
 * @author  Lukasz Korzybski (lukasz.korzybski@gmail.com)
 * @version 0.2
 * @copyright PERFEKT (http://www.bperfekt.pl)
 */

(function($) {
	
	$.fn.jFlashTube = function(options) {
		var opts = $.extend({} ,$.fn.jFlashTube.defaults, options);
		var jmediaNum = 0;
		
		return this.each(function() {
			var jft = $(this);
			var jctrl = jft.find('.'+opts.ctrlClass+':first');
			var jview = getViewElement(jft, opts);
			
			jview.attr('id', 'jflashtube_' + jmediaNum++);
			var player = createPlayer(jview, jctrl, opts);
			
			if (opts.applyCSS) {
				applyDefaultCSS(jctrl, opts);
			}
			
			$('li', jctrl).click(function() {
				
				player.play(clipConfig(this, jctrl, opts));
				return false;
			});
		// eof main loop
		});
	};
	
	var createPlayer = function(jview, jctrl, opts) {
		var initConfig = {};
		
		if (jctrl.find('li').length) { initConfig.clip = clipConfig(jctrl.find('li:first').get(0), jctrl, opts); }
		if (opts.key) { initConfig.key = opts.key; }
		
		$.extend(initConfig, opts.extra);
		
		return jview.flowplayer(opts.playerURL, initConfig).flowplayer(0);
	}
	
	var clipConfig = function(li, jctrl, opts) {
		var video = getVideoURL(li, jctrl, opts);
		var clip = {
				autoPlay: opts.autoPlay, 
				scaling: opts.initialScale,
				url: video.url,
				onFinish : function() { this.stop(); }
		};
		$.extend(clip, opts.extraClip);
		
		return clip;
	};
	
	var getVideoURL = function(li, jctrl, opts) {
		var videoURL = $('a:eq(0)', li).attr('href');
		var videoQS = getQS(videoURL);
		
		if (!flashembed.isSupported(opts.flashVersion)) {
			opts.oldVersionNotif(getViewElement(jctrl, opts).attr('id'));
			
			if (opts.fallback) {
				if ('fallback' in videoQS) {
					videoURL = videoQS.fallback;
				}
				else if (opts.fbRegexp != null) {
					videoURL = videoURL.replace(opts.fbRegexp[0], opts.fbRegexp[1]);
				}
			}
		}
		return { url: videoURL, qs: videoQS };
	};
	
	
	var getQS = function(url) {
		var qs = {};
		var t = url.split('?');
		if (t.length == 2) {
			var parms = t[1].split('&');
			$.each(parms, function(i, v){
				var pair = v.split('=');
				if (pair.length == 2 && pair[0] && pair[1]) {
					qs[pair[0]] = pair[1];
				}
			});
		}
		return qs;
	};
	
	
	var getViewElement = function(jft, opts) {
		var view = jft.find('.'+opts.viewClass);
		if (view.length == 0) {
			jft.find('.'+opts.ctrlClass).before('<div class="' + opts.viewClass + '">' + (opts.useSplash ? '&nbsp;' : '') + '</div>');
			return jft.find('.'+opts.viewClass+':first');
		} else { 
			return $(view.get(0));
		}
	};
	
	
	var applyDefaultCSS = function(jctrl, opts) {
		$('li', jctrl).mouseover(function() { 
				$(this).addClass(opts.hoverClass)  
			}).mouseout(function() { 
				$(this).removeClass(opts.hoverClass); 
		});
	};
	
	
	// plugin defaults
	$.fn.jFlashTube.defaults = {
		playerURL 	: '/flash/flowplayer/flowplayer.swf',
		viewClass	: 'jftView',
		ctrlClass   : 'jftCtrl',
		initialScale: 'fit',
		key			: '',
		autoPlay	: true,
		useSplash   : true,
		fallback	: true,
		flashVersion : [9, 124],
		oldVersionNotif  : function(viewId) {}, // callback function for old flash version notification, view's id is passed
		fbRegexp 	: null, // [regexp, repl_str] - used when no fallback param found in video url
		
		applyCSS    : true,
		hoverClass  : 'jftHover',
		thumbWidth  : 100,
		
		extra		: {},
		extraClip   : {}
	};
	
})(jQuery);
