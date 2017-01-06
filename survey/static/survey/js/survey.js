$(function() {
	// markdown format content of each md classed element
	$( ".md" ).each(function( index ) {
		$( this ).html(marked( $( this ).html() ));
	});
});

$('.md_form').on('keyup', function(event){
	//update preview
	var title = $('#id_title').val();
	var textarea = "";
	if($('#id_text').val() === undefined){
		textarea = $('#id_description').val();
	}
	else {
		textarea = $('#id_text').val();
	}
	$("#title").html(title);
	$("#preview").html(marked(textarea));
})