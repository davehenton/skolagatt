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

    $(document).on('click', "a[data-action='save_notes']", function(event){
    	$.ajax({
        url : "create_post/", // the endpoint
        type : "POST", // http method
        data : {
        	'ssn': $('#ssn').html(),
        	'notes':$('#student-notes').val(),
        	'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').attr("value"),
        	}, // data sent with the post request

        // handle a successful response
        success : function(json) {
            console.log("success"); // another sanity check
        },

        // handle a non-successful response
        error : function(xhr,errmsg,err) {
            console.log("error"); // provide a bit more info about the error to the console
        }
    	});
    });

    $('#save_exception').on('click', function(event){
        //event.preventDefault();
        if( !$('input[name="reason"]:checked').val()){
            alert('Það þarf að velja ástæðu');
            event.preventDefault();
            return;
        }
        exam_array = [];
        for(i= 0; i < $("#id_exam_2").val(); i++)
        {
            if ($('#id_exam_'+i).is(":checked"))
            {
                exam_array.push(parseInt($('#id_exam_'+i).val()));
            }
        };
        console.log(exam_array)
        if(exam_array.length == 0){
            alert('Þarft að velja próf');
            event.preventDefault();
            return;
        }
        $.ajax({
        url : "exception_post/", // the endpoint
        type : "POST", // http method
        data : {
            'notes': $('#notes').val(),
            'expl': $('#explanation').val(),
            'exam': JSON.stringify(exam_array),
            'reason': $('input[name="reason"]:checked').val(),
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').attr("value"),
            }, // data sent with the post request

        // handle a successful response
        success : function(json) {
            $(this).attr('href');
            console.log(exam_array);
            //event.preventDefault();
        },

        // handle a non-successful response
        error : function(xhr,errmsg,err) {
            console.log("error"); // provide a bit more info about the error to the console
            console.log(exam_array);
            //event.preventDefault();
        }
        });
    });

    $(document).on('click', "a[data-action='cancel_exception']", function(event){
        var x;
        if (confirm("Ertu viss um að þú viljir eyða þessari undanþágu") == false) {
            event.preventDefault();
            return;
        }
        $.ajax({
        url : "exception_cancel/", // the endpoint
        type : "POST", // http method
        data : {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').attr("value"),
            }, // data sent with the post request

        // handle a successful response
        success : function(json) {
            $(this).attr('href');
        },

        // handle a non-successful response
        error : function(xhr,errmsg,err) {
            console.log("error"); // provide a bit more info about the error to the console
        }
        });
    });

});