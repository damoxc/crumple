/*!
 * LoginWindow.js
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

Crumple.LoginWindow = Ext.extend(Ext.Window, {

	title: 'Welcome to Crumple Mail',
	modal: true,
	width: 400,
	height: 150,
	
	initComponent: function() {
		Crumple.LoginWindow.superclass.initComponent.call(this);
		this.form = this.add({
			xtype: 'form',
			height: 250,
			border: false,
			bodyStyle: 'padding: 5px;',
			ctCls: 'x-plain',
			defaultType: 'textfield',
			defaults: {
				width: 250
			},
			items: [{
				name: 'username',
				fieldLabel: 'Username'
			}, {
				name: 'password',
				inputType: 'password',
				fieldLabel: 'Password'
			}, {
				name: 'server',
				fieldLabel: 'Server'
			}]
		});
		this.addButton('Login', this.onLogin, this);
	},

	onLogin: function() {
		var fv = this.form.getForm().getValues();
		crumple.client.core.login(fv.username, fv.password, fv.server, {
			success: function(result) {
				alert(result);
			}
		});
	}

});
