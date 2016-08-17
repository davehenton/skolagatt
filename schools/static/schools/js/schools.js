
jQuery.fn.filterByText = function(textbox, selectSingleMatch, year) {
	return this.each(function() {
		var select = this;
		var options = [];
		$(select).find('option').each(function() {
			options.push({value: $(this).val(), text: $(this).text()});
		});
		$(select).data('options', options);
		$(textbox).bind('change keyup', function() {
			var options = $(select).empty().scrollTop(0).data('options');
			var search = $.trim($(this).val());
			var regex = new RegExp(search,'gi');
	 
			$.each(options, function(i) {
				var option = options[i];
				data = option.text;
				if(year)
				{
					data = data.substring(5,7);
				}
				if(data.match(regex) !== null) {
					$(select).append(
						$('<option>').text(option.text).val(option.value)
					);
				}
			});
			if (selectSingleMatch === true && 
				$(select).children().length === 1) {
					$(select).children().get(0).selected = true;
			}
		});
	});
};

$(function() {
	// markdown format content of each md classed element
	$( ".md" ).each(function( index ) {
		$( this ).html(marked( $( this ).html() ));
	});
});

//filter all_students by name
$(function() {
	$('#all_students').filterByText($("#search_students"), false, false);
}); 

//filter all_students by name
$(function() {
	$('#all_students').filterByText($("#search_year"), false, true);
}); 


$(document).ready(function() {
	$(document.body).on('click', '#message-header', function(){ 
		var details = $(this).nextUntil('#message-header').toggle();
    });
	

	$("#notes").on('click',function(){
		if($('#textareaid').is(":visible"))
		{
			var r = confirm("Viltu vista skilaboðin?");
			if (r == true) {

				$.post("notes_save/",{notes: $("#textareaid").val(), 'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').attr("value")},function(result){
					$('div#notesshow').text($("#textareaid").val());
				});
			}
		}
    	$('#notesshow').toggle();
    	$('#textareashow').toggle();

    });

    $(document).on('click', "a[data-action='save_notes']", function(event){
    	if($('#textareaid').is(":visible"))
		{
			var r = confirm("Viltu vista skilaboðin?");
			if (r == true) {

				$.post("notes_save/",{notes: $("#textareaid").val(), 'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').attr("value")},function(result){

				});
			}
		}
    });

    $('body').on('click', 'option', function() {
		$(this).toggleClass('selected');
	});

	$('#move_left').click(function() {
		$('#all_students').append($('#group_students .selected').removeClass('selected'));

	});

	$('#move_right').click(function() {
		$('#group_students').append($('#all_students .selected').removeClass('selected'));
		$("#group_students option").removeAttr('selected');
	});

	$('#teacher_move_left').click(function() {
		$('#all_teachers').append($('#group_managers .selected').removeClass('selected'));
	});

	$('#teacher_move_right').click(function() {
		$('#group_managers').append($('#all_teachers .selected').removeClass('selected'));
		$("#group_managers option").removeAttr('selected');
	});

	$('#studentgroup').submit(function(){
		if($("#id_name").val()=="")
		{
			alert('Gleymdir að fylla inn nafnið');
			return false;
		}
		if($("#id_student_year").val()=="")
		{
			alert('Gleymdir að fylla inn námsár')
			return false;
		}
		$("#group_students option").prop('selected',true);
		$("#group_managers option").prop('selected',true);

	});
});

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
			options += '<option value=' + value['pk'] + '>' + value['title'] + ' - ' + value['active_to'] + '</option>';
		});
		select.append(options);
		var s = $('#id_survey').parent().before(select);
	}
	catch(err) {	}
});

