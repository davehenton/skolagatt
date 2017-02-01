$(document).ready(function() {
    /*$('table#student_list tr').click(function(){
        window.location = $(this).attr('href');
        return false;
    });*/

    if ( typeof pagetype !== 'undefined' && pagetype == 'exceptions' ) {
        $("#id_exempt").prop('checked', exempt)
    }

    if ( typeof pagetype !== 'undefined' && pagetype == 'supportresource' ) {
        $("#id_reading_assistance").prop('checked', reading_assistance);
        $("#id_interpretation".prop('checked', interpretation);
        $("#id_longer_time").prop('checked', longer_time);
    }




    $(document).on('click', "button[value='exceptiondelete']", function(event){
        if (confirm("Ertu viss um að þú viljir eyða þessari undanþágu") == false) {
            event.preventDefault();
            return;
        }
    });

    $(document).on('click', "button[value='supportdelete']", function(event){
        if (confirm("Ertu viss um að þú viljir eyða þessum stuðningsúrræðum") == false) {
            event.preventDefault();
            return;
        }
    });

});
