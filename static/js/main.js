$(document).ready(function() {
	$('table#student_list tr').click(function(){
        window.location = $(this).attr('href');
        return false;
    });

});
var datafy_table = function(table) {
	$(table).DataTable({
		"bLengthChange": false,
	    "pageLength": 20,
		"language": {
		    "sEmptyTable":     "Engin gögn eru í þessari töflu",
		    "sInfo":           '',
		    "sInfoEmpty":      "0 færslur",
		    "sInfoFiltered":   "(síað út frá _MAX_ færslum)",
		    "sInfoPostFix":    "",
		    "sInfoThousands":  ".",
		    "sLengthMenu":     "Sýna _MENU_ færslur",
		    "sLoadingRecords": "Hleð...",
		    "sProcessing":     "Úrvinnsla...",
		    "sSearch":         "Leita:",
		    "sZeroRecords":    "Engar færslur fundust",
		    "oPaginate": {
		        "sFirst":    "Fyrsta",
		        "sLast":     "Síðasta",
		        "sNext":     "Næsta",
		        "sPrevious": "Fyrri"
		    },
		    "oAria": {
		        "sSortAscending":  ": virkja til að raða dálki í hækkandi röð",
		        "sSortDescending": ": virkja til að raða dálki lækkandi í röð"
		    }
		}
	});
}