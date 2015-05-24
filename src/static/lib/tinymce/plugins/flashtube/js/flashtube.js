FlashTube = {};

(function(module) {
	tinyMCEPopup.requireLangPack();

	var FlashTubeDialog = {
		init : function() {
			this.videoNum = 4;
		},
		
		insert : function() {
			var editor = tinyMCEPopup.editor;
			var dom = tinyMCEPopup.dom;
			var i = 1;
			var titleLinks = dom.get('id_titles').checked;
			var ul = dom.create('ul', { 'class' : 'jftCtrl' + (titleLinks ? ' titles' : '') });
			
			while (dom.get('id_title'+i) != null) {
				var url = dom.get('id_url'+i).value;
				var title = dom.get('id_title'+i).value;
				if (!url) {
					i++; continue;
				}
				
				var thumbUrl = url.replace(editor.getParam('flashtube_thumb_regexp', /(.*)_\w+\.(\w*)$/), 
										   editor.getParam('flashtube_thumb_repl', '$1_thumb.jpg'));
				var fallbackUrl = url.replace(editor.getParam('flashtube_fallback_regexp', /(.*)_\w+\.(\w*)$/),
											  editor.getParam('flashtube_fallback_repl', '$1_low.$2'));
				var li = dom.create('li');
				
				var avars = { href : url+'?fallback='+fallbackUrl };
				if (titleLinks == false) { avars.title = title; }
				
				var a = dom.create('a', avars);
				dom.add(a, dom.create('img', { src : thumbUrl, alt : title }));
				dom.add(li, a);
				
				if (titleLinks) {
					var div = dom.create('div');
					dom.add(div, dom.create('a', {
						href: url
					}, title));
					dom.add(li, div);
				}
				
				dom.add(ul, li);
				i++;
			}
			
			var container = dom.create('div', { 'class' : 'flashTube' });
			if (editor.getParam('flashtube_createview', true)) {
				dom.add(container, dom.create('div', { 'class': 'jftView' }, '&nbsp;'));
				
			}
			dom.add(container, ul);
			
			if (editor.getParam('flashtube_float_clear', true)) {
				dom.add(container, dom.create('div', { 'style' : 'clear: both' }, '&nbsp'));
			}
			
			editor.selection.setNode(container);
			tinyMCEPopup.close();
		},
		
		addVideo : function() {
			var editor = tinyMCEPopup.editor;
			var dom = tinyMCEPopup.dom;
			var container = dom.get('add_videos');
			
			this.videoNum++;
			dom.add(container, dom.create('p'), {}, '<strong>'+editor.getLang('flashtube_dlg.video')+' '+this.videoNum+'</strong>');
			
			var ul = dom.create('ul');
			var p = ['url', 'title'];
			for (i in p) {
				var li = dom.create('li');
				dom.add(li, dom.create('label', { 'for' : 'id_'+p[i]+this.videoNum }, editor.getLang('flashtube_dlg.'+p[i])));
				dom.add(li, dom.create('input', { 'id': 'id_'+p[i]+this.videoNum, 'type': 'text', 'name': p[i]+this.videoNum, 'class': 'text'}));
				dom.add(ul, li);	
			}
			dom.add(container, ul);
		}
	};
	
	tinyMCEPopup.onInit.add(FlashTubeDialog.init, FlashTubeDialog);

	module.dialog = FlashTubeDialog;

})(FlashTube);