/*!
 * Crumple.Sidebar.js
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
Ext.ns('Crumple')

Crumple.Sidebar = Ext.extend(Ext.Panel, {

	width: 200,
	region: 'west',
	split: true,
	layout: 'border',
	
	initComponent: function() {
		Crumple.Sidebar.superclass.initComponent.call(this);

		this.contentPanel = this.add({
			title: 'Mail',
			region: 'center'
		});

		this.buttonsPanel = this.add({	
			defaultType: 'button',
			defaults: {
				width: '100%'
			},
			region: 'south',
			autoHeight: true
		});

		this.buttonsPanel.add({
			text: 'Mail'
		});
		this.buttonsPanel.add({
			text: 'Contacts'
		});
	}
	
});
