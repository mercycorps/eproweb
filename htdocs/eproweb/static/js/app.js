
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
        //console.log("settings: " + settings);
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
 * Returns params in the URL.
 */
function getUrlVars() {
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < hashes.length; i++)
    {
        hash = hashes[i].split('=');
        vars.push(hash[0]);
        vars[hash[0]] = hash[1];
    }
    return vars;
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