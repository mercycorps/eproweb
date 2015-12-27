
$(document).ready(function() { 

});

var $loading = $('#loading');

/* 
 * A global ajaxComplete method that shows you any messages that are set in Django's view
 */
$( document )
    .ajaxStart( function() {
        $loading.show();
    })
    .ajaxStop( function() {
        $loading.hide();
    })
    .ajaxComplete(function(e, xhr, settings) {
        var contentType = xhr.getResponseHeader("Content-Type");
        if (contentType == "application/javascript" || contentType == "application/json") {
            var json = $.parseJSON(xhr.responseText);
            show_django_ajax_messages(json);
        }
    })
    .ajaxError(function(e, xhr, settings, thrownError) {
        createAlert("danger", "Error " + xhr.status + ": " +  thrownError, false);
    });


function show_django_ajax_messages(json, whereToAppend) {
    if (json.django_messages != undefined) {
        $.each(json.django_messages, function (i, item) {
            createAlert(item.extra_tags, item.message, true, whereToAppend);
        });
    }
}


/* 
 * Every time the Country dropdown changes, update the Office dropdown options
 */
$('body').on('change', 'select#id_country', function(e) {
    update_office_select($(this).val());
    update_currency_select($(this).val());
});


/*
 * Show relevant offices for the selected country dropdown.
 */
function update_office_select(country_id) {
    //$("#div_id_office").find("span#select2-chosen-2").filter(':visible:first').text("---------");
    var url = '/api/v1/offices/?country=' + country_id;
    $.getJSON(url, function(offices) {
        var options = "<option value=''></option>"; //"<option value=''>---------</option>";
        for (var i = 0; i < offices.length; i++) {
            options += '<option value="' + offices[i].id + '">' + offices[i].name + '</option>';
        }
        $("select#id_office").html(options);
        //$("select#id_office option:first").attr('selected', 'selected');
        $("select#id_office").val('').trigger("change");
    });
    return true;
}


/*
 * Show relevant currencies for the selected country dropdown.
 */
function update_currency_select(country_id) {
    //$("#div_id_currency").find("span#select2-chosen-2").filter(':visible:first').text("---------");
    var url = '/api/v1/currencies/?country=' + country_id;
    $.getJSON(url, function(currencies) {
        var options = "<option value=''></option>"; //"<option value=''>---------</option>";
        for (var i = 0; i < currencies.length; i++) {
            options += '<option value="' + currencies[i].id + '">' + currencies[i].code + '</option>';
        }
        $("select#id_currency").html(options);
        //$("select#id_currency option:first").attr('selected', 'selected');
        $("select#id_currency").val('').trigger("change");
    });
    return true;
}


$('body').on('click', 'a#add_new_pr_link, a#pr_edit_btn', function(e) {
    e.preventDefault();
    $("#app_modal_div_content_div").load($(this).attr("href"));
    $('#app_modal_div').modal('show');
});



$('#confirm-delete').on('show.bs.modal', function(e) {
    $(this).find('.btn-ok').attr('href', $(e.relatedTarget).data('href'));

    $('.debug-url').html('Delete URL: <strong>' + $(this).find('.btn-ok').attr('href') + '</strong>');
});


// Submit FinanceCodes Form via AJAX for adding and editing of finance codes.
$('body').on('submit', '#id_prform', function(event) {
    event.preventDefault();
    var form_url = $(this).attr('action');
    var form_data = $(this).serialize();

    $.post(form_url, form_data)
        .done(function(data, textStatus, jqXHR) {
            if (jqXHR.getResponseHeader('error') == "True") {
                $("#app_modal_div_content_div").html(data);
            } else {
                $('#app_modal_div').modal('hide');
            }
        });
});

/*
 * Create and show a Bootstrap alert.
 */
function createAlert (type, message, fade, whereToAppend) {
    if (whereToAppend == undefined ){
        whereToAppend = "#messages";
    }
    $(whereToAppend).append(
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