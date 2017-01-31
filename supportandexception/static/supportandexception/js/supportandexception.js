$(document).ready(function() {
    /*$('table#student_list tr').click(function(){
        window.location = $(this).attr('href');
        return false;
    });*/

    if ( typeof pagetype !== 'undefined' && pagetype == 'exceptions' ) {
        $("#id_exempt").prop('checked', exempt)
    }

    if ( typeof pagetype !== 'undefined' && pagetype == 'supportresource' ) {
        for(i=1; i < 4 ; i++ ){
            if ($.inArray( i, reading_assistance )!=-1)
            {
                $("#id_reading_assistance_"+(i-1)).prop('checked',true);
            }
            if ($.inArray( i, interpretation )!=-1)
            {
                $("#id_interpretation_"+(i-1)).prop('checked',true);
            }
            if ($.inArray( i, longer_time )!=-1)
            {
                $("#id_longer_time_"+(i-1)).prop('checked',true);
            }
        }
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
