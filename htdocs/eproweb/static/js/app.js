
$(document).ready(function() { 
    update_office_select($("#id_country").val());
    update_currency_select($("#id_country").val());

    $("#id_country").select2({ allowClear: true, });
    $("#id_office").select2({ allowClear: true, });
    $("#id_currency").select2({ allowClear: true, });
    $("#id_approver1").select2({ allowClear: true, });
    $("#id_approver2").select2({ allowClear: true, });
});


/* 
 * Every time the Country dropdown changes, update the Office dropdown options
 */
$('body').on('change', 'select#id_country', function() {
    update_office_select($(this).val());
    update_currency_select($(this).val());
});


/*
 * Show relevant offices for the selected country dropdown.
 */
function update_office_select(country_id) {
    $("#div_id_office").find("span#select2-chosen-2").filter(':visible:first').text("---------");
    var url = '/api/v1/offices/?country=' + country_id;
    $.getJSON(url, function(offices) {
        var options = "<option value=''>---------</option>";
        for (var i = 0; i < offices.length; i++) {
            options += '<option value="' + offices[i].id + '">' + offices[i].name + '</option>';
        }
        $("select#id_office").html(options);
        $("select#id_office option:first").attr('selected', 'selected'); 
    });
}


/*
 * Show relevant currencies for the selected country dropdown.
 */
function update_currency_select(country_id) {
    $("#div_id_currency").find("span#select2-chosen-2").filter(':visible:first').text("---------");
    var url = '/api/v1/currencies/?country=' + country_id;
    $.getJSON(url, function(currencies) {
        var options = "<option value=''>---------</option>";
        for (var i = 0; i < currencies.length; i++) {
            options += '<option value="' + currencies[i].id + '">' + currencies[i].code + '</option>';
        }
        $("select#id_currency").html(options);
        $("select#id_currency option:first").attr('selected', 'selected'); 
    });
}


/*
 * Create and show a Bootstrap alert.
 */
function createAlert (type, message, fade) {
    $("#messages").append(
        $(
            "<div class='alert alert-" + type + " dynamic-alert alert-dismissable'>" +
            "<button type='button' class='close' data-dismiss='alert' aria-hidden='true'>&times;</button>" +
            "<p>" + message + "</p>" +
            "</div>"
        )
    );
    if (fade == true) {
        // Remove the alert after 5 seconds if the user does not close it.
        $(".dynamic-alert").delay(5000).fadeOut("slow", function () { $(this).remove(); });
    }
}


/*
 * Get a cookie by name.
 */
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

/*
 * Set the csrf header before sending the actual ajax request
 * while protecting csrf token from being sent to other domains
 */
$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});