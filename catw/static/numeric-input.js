/* global $ $UPDATE_URL */
/* 
This file is based on the numeric-input-example.js
https://github.com/mindmup/editable-table/blob/master/numeric-input-example.js
.on('validate') method is removed. This method allows to modify the first column
on the table, which is not a requirement for this project.
*/
$.fn.numericInput = function () {
	'use strict';
	var element = $(this),
		footer = element.find('tfoot tr'),
		dataRows = element.find('tbody tr'),
		initialTotal = function () {
			var column, total;
			for (column = 1; column < footer.children().size()-1; column++) {
				total = 0;
				dataRows.each(function () {
					var row = $(this);
					total += parseFloat(row.children().eq(column).text());
				});
				footer.children().eq(column).text(total);
			};
			weektotal();
		},
		weektotal = function() {
			var column, total = 0;
			for (column = 1; column < footer.children().size()-1; column++) {
				total += parseFloat(footer.children().eq(column).text());
			}
			footer.children().eq(8).text(total);
		};
	element.find('td').on('change', function () {
		var cell = $(this),
			column = cell.index(),
			total = 0;
		if (column === 0) {
			return;
		}
		// This will be send to the server
		var dtstr = "dbid=" + cell.attr('dbid') + "&ts=" + cell.text();
		$.ajax({
			url: $UPDATE_URL,
			data: dtstr
		});
		element.find('tbody tr').each(function () {
			var row = $(this);
			total += parseFloat(row.children().eq(column).text());
		});
		footer.children().eq(column).text(total);
		weektotal();
	});
	/* I can't validate for numeric, so accept it but refuse it on Server side */
	initialTotal();
	return this;
};