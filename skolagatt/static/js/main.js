$(function() {
    // markdown format content of each md classed element
    $( ".md" ).each(function( index ) {
        $( this ).html(marked( $( this ).html() ));
    });
});