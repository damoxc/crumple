Ext.apply(Ext, {
	keys: function(obj) {
		var keys = [];
		for (var k in obj) {
			if (!obj.hasOwnProperty(k)) continue;
			keys.push(k);
		}
		return keys;
	},

	values: function(obj) {
		var values = [];
		for (var k in obj) {
			if (!obj.hasOwnProperty(k)) continue;
			values.push(obj[k]);
		}
		return values;
	}
});
Ext.BLANK_IMAGE_URL = '/images/s.gif';
Ext.USE_NATIVE_JSON = true;
