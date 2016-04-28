function update_form(data) {
	$('#id_survey').val(data[0]['pk']);
	$('#id_title').val(data[0]['title']);
	$('#id_active_from').val(data[0]['active_from']);
	$('#id_active_to').val(data[0]['active_to']);
	$('#id_data_fields').val(JSON.stringify(data[0]['data_fields']));
}

function clear_form() {
	$('#id_survey').val('');
	$('#id_title').val('');
	$('#id_active_from').val('');
	$('#id_active_to').val('');
	$('#id_data_fields').val('');
}


$( document ).on("change", "#survey_select", function(){
	var survey_id = $( "#survey_select option:selected" ).val();
	if(survey_id !== "") {
		data = $.grep(survey_list, function(e){ return e.pk == survey_id; });
		update_form( data );
	}
	else {
		//clear_form();
	}
});

$(function() {
	try {
		//add namska select
		var select = $("<select id=\"survey_select\" name=\"survey_select\" />");
		var options= '<option value="">Velja könnun</option>';
		$.each(survey_list, function(key, value){
			options += '<option value=' + value['pk'] + '>' + value['title'] + '</option>';
		});
		select.append(options);
		var s = $('#id_survey').parent().before(select);
	}
	catch(err) {	}
});