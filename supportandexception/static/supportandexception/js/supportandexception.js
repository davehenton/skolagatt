$(document).ready(function() {
    $('table#student_list tr').click(function(){
        window.location = $(this).attr('href');
        return false;
    });

    if ( typeof pagetype !== 'undefined' && pagetype == 'exceptions' ) {
        for(i=1; i < 4 ; i++ ){
            if ($.inArray( i, exam )!=-1)
            {
                $("#id_exam_"+(i-1)).prop('checked',true);
            }
            if ($.inArray( i, reason )!=-1)
            {
                $("#id_reason_"+(i-1)).prop('checked',true);
            }
        }
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
            if ($.inArray( i, return_to_sites )!=-1)
            {
                $("#id_return_to_sites_"+(i-1)).prop('checked',true);
            }
            if ($.inArray( i, longer_time )!=-1)
            {
                $("#id_longer_time_"+(i-1)).prop('checked',true);
            }
        }
    }

    $(exception).on('click', function(event){
    	if($('button[value="exceptionsave"]').val()){

    	};
        if( !$('input[name="reason"]:checked').val()){
            alert('Það þarf að velja ástæðu');
            event.preventDefault();
            return;
        };
        this.submit();
    });

	$(document).on('click',"button[value='exceptiondelete']", function(event){
        //event.preventDefault();
        alert('kalli');
        if( !$('input[name="reason"]:checked').val()){
            alert('Það þarf að velja ástæðu');
            event.preventDefault();
            return;
        }
    });

    $(document).on('click', "a[data-action='cancel_exception']", function(event){
        if (confirm("Ertu viss um að þú viljir eyða þessari undanþágu") == false) {
            event.preventDefault();
            return;
        }
    });

});
