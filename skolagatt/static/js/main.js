$(function() {
    // markdown format content of each md classed element
    $( ".md" ).each(function( index ) {
        $( this ).html(marked( $( this ).html() ));
    });
});

/* Function to strip html from strings. Table sorting needs it. */
function html_strip(str) {
	var htmre = /(<([^>]+)>)/ig;
	str = str.toString();
	return str.replace(htmre, '');
}

/*
 * The following code was adapted from the great icelandic library found at
 * https://github.com/islenska-org/icelandic
 *
 * Sorting in Icelandic would suck without it.
 */
var alphabetIndex = {};
// Icelandic sorts lowercase before uppercase
' -.,0123456789aábcdðeéfghiíjklmnoópqrstuúvwxyýzþæö'
  .split( '' )
  .forEach( ( d, i ) => {
    alphabetIndex[d] = i + 1;
    if ( d.toUpperCase() !== d ) {
      alphabetIndex[d.toUpperCase()] = i + 1;
    }
  });


function icelandic_alphabet( a, b, html ) {
  // Strip html if it's there
  if (html) {
  	a = html_strip(a);
  	b = html_strip(b);
  }
  // same word? exit early
  var al = a.length;
  var bl = b.length;
  if ( al === bl && a === b ) {
    return 0;
  }
  // char by char evaluation
  var l = Math.min( al, bl );
  var c = -1;
  while ( ++c < l ) {
    var aV = alphabetIndex[a[c]];
    var bV = alphabetIndex[b[c]];
    // because iceN has a 1 based index, any falsy value means "undefined" character
    if ( !aV || !bV ) {
      // either char is not defined: we can JS sort them
      return a[c] < b[c] ? -1 : a[c] > b[c] ? 1 : 0;
    }
    else if ( aV !== bV ) {
      // it's not the same char, go by value
      return aV - bV;
    }
  }
  // words are not identical but didn't sort: this must be the same word but casing is different!
  if ( al === bl ) {
    return a > b ? -1 : a < b ? 1 : 0;
  }
  // words are not identical, so the longer one is the shorter+suffix
  return al - bl;
};

/* ==================== END OF ICELANDIC CODE ==================== */

function reformat_kt(kt) {
	if (kt[9] === "9") {
		return kt.replace( /(\d{2})(\d{2})(\d{2})\d+/, "19$3$2$1")
	}
	else {
		return kt.replace( /(\d{2})(\d{2})(\d{2})\d+/, "20$3$2$1")
	}
}
function kt_sort(a, b, html) {
	// Strip html if it's there
    if (html) {
  	    a = html_strip(a);
  	    b = html_strip(b);
    }
    a = reformat_kt(a);
    b = reformat_kt(b);
    return (a < b) ? -1 : ((a > b) ? 1 : 0)
}
/*
 * The rest is to extend the DataTables JS library for better table sorting.
 */

jQuery.extend( jQuery.fn.dataTableExt.oSort, {
    "icelandic-asc": function ( a, b ) {
        return icelandic_alphabet(a, b, false);
    },
    "icelandic-desc": function ( a, b ) {
        return icelandic_alphabet(a, b, false) * -1;
    },
    "icelandic-html-asc": function ( a, b ) {
        return icelandic_alphabet(a, b, true);
    },
    "icelandic-html-desc": function ( a, b ) {
        return icelandic_alphabet(a, b, true) * -1;
    },
    "num-html-pre": function ( a ) {
        var x = String(a).replace( /<[\s\S]*?>/g, "" );
        return parseFloat( x );
    },
    "num-html-asc": function ( a, b ) {
        return ((a < b) ? -1 : ((a > b) ? 1 : 0));
    },
    "num-html-desc": function ( a, b ) {
        return ((a < b) ? 1 : ((a > b) ? -1 : 0));
    },
    "kt-asc": function ( a, b ) {
        return kt_sort(a, b, false);
    },
    "kt-desc": function ( a, b ) {
        return kt_sort(a, b, false) * -1;
    },
    "kt-html-asc": function ( a, b ) {
        return kt_sort(a, b, true);
    },
    "kt-html-desc": function ( a, b ) {
        return kt_sort(a, b, true) * -1;
    },
} );

var dataTable_settings = {
	"bLengthChange": false,
    "pageLength": 20,
	"language": {
	    "sEmptyTable":     "Engin gögn eru í þessari töflu",
	    "sInfo":           '',
	    "sInfoEmpty":      "",
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
};
