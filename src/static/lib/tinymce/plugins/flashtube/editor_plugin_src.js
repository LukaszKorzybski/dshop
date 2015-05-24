/**
 * $Id: editor_plugin_src.js 201 2007-02-12 15:56:56Z spocke $
 *
 * @author Moxiecode
 * @copyright Copyright � 2004-2008, Moxiecode Systems AB, All rights reserved.
 */

(function() {
	// Load plugin specific language pack
	tinymce.PluginManager.requireLangPack('flashtube');

	tinymce.create('tinymce.plugins.FlashTubePlugin', {
		/**
		 * @param {tinymce.Editor} ed Editor instance that the plugin is initialized in.
		 * @param {string} url Absolute URL to where the plugin is located.
		 */
		init : function(ed, url) {
			// Register the command so that it can be invoked by using tinyMCE.activeEditor.execCommand('mceFlashTube');
			ed.addCommand('mceFlashTube', function() {
				ed.windowManager.open({
					file : url + '/flashtube.htm',
					width : 550 + parseInt(ed.getLang('flashtube.delta_width', 0)),
					height : 470 + parseInt(ed.getLang('flashtube.delta_height', 0)),
					inline : 1
				}, {
					plugin_url : url, // Plugin absolute URL
					some_custom_arg : 'custom arg' // Custom argument
				});
			});

			// Register FlashTube button
			ed.addButton('flashtube', {
				title : 'flashtube.desc',
				cmd : 'mceFlashTube',
				image : url + '/img/flashtube.gif'
			});

			// Add a node change handler, selects the button in the UI when a image is selected
			//ed.onNodeChange.add(function(ed, cm, n) {
			//	cm.setActive('flashtube', n.nodeName == 'IMG');
			//});
		},

		/**
		 * Creates control instances based in the incomming name. This method is normally not
		 * needed since the addButton method of the tinymce.Editor class is a more easy way of adding buttons
		 * but you sometimes need to create more complex controls like listboxes, split buttons etc then this
		 * method can be used to create those.
		 *
		 * @param {String} n Name of the control to create.
		 * @param {tinymce.ControlManager} cm Control manager to use inorder to create new control.
		 * @return {tinymce.ui.Control} New control instance or null if no control was created.
		 */
		createControl : function(n, cm) {
			return null;
		},

		/**
		 * Returns information about the plugin as a name/value array.
		 * The current keys are longname, author, authorurl, infourl and version.
		 *
		 * @return {Object} Name/value array containing information about the plugin.
		 */
		getInfo : function() {
			return {
				longname : 'FlashTube plugin',
				author : 'Lukasz Korzybski',
				authorurl : 'http://bprefekt.pl',
				infourl : 'http://wiki.moxiecode.com/index.php/TinyMCE:Plugins/example',
				version : "0.1"
			};
		}
	});

	// Register plugin
	tinymce.PluginManager.add('flashtube', tinymce.plugins.FlashTubePlugin);
})();