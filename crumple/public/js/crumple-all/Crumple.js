/*!
 * Crumple.js
 * 
 * Copyright (c) Damien Churchill 2010 <damoxc@gmail.com>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, write to:
 *     The Free Software Foundation, Inc.,
 *     51 Franklin Street, Fifth Floor
 *     Boston, MA  02110-1301, USA.
 */

Ext.apply(crumple, {

	content: null,

	sidebar: null,

	statusbar: null,
	
	initialize: function(e) {
		
		this.content = new Ext.Container({
			autoDestroy: false,
			region: 'center',
			layout: 'card'
		});

		this.sidebar = new Ext.Panel({
			width: 200,
			region: 'west',
			split: true,
			layout: 'accordion'
		});

		this.statusbar = new Ext.ux.StatusBar({
			text: 'Crumple v' + this.version
		});
		
		this.panel = new Ext.Panel({
			layout: 'border',
			items: [this.sidebar, this.content],
			bbar: this.statusbar,
			border: false
		});

		this.viewport = new Ext.Viewport({
			layout: 'fit',
			items: [this.panel],
			border: false
		});

		this.mail = new Crumple.mail.MailController();
		this.mail.initialize();

		this.loginWindow = new Crumple.LoginWindow();

		this.client = new Ext.ux.util.RpcClient({
			url: '/json'
		});
		this.client.on('connected', function(e) {
			this.loginWindow.show();
		}, this, {single: true});
	}
});

Ext.onReady(function() {
	crumple.initialize();
});
