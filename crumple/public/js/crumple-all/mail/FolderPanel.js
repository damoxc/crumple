/*!
 * mail/FolderPanel.js.js
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

Ext.ns('Crumple.mail');

Crumple.mail.FolderPanel = Ext.extend(Ext.Panel, {
	
	title: 'Mail',
	border: false,
	
	initComponent: function() {
		Crumple.mail.FolderPanel.superclass.initComponent.call(this);
	}

});
