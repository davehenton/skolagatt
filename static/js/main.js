$(document).ready(function() {
	$('table#student_list tr').click(function(){
        window.location = $(this).attr('href');
        return false;
    });

    $("#kalli").click(function(){
    	alert("I am an alert box!");
    });

});