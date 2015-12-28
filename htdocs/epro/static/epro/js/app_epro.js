
$(document).ready(function() { 
    alert("OK");
});


/* 
 * Every time the Country dropdown changes, update the Office dropdown options
 */
$('body').on('change', 'select#id_country', function(e) {
    update_originating_office($(this).val());
    update_pr_currency($(this).val());
});




function update_originating_office(country_id) {
    var url = '/api/v1/offices/?country=' + country_id;
    var office_dropdown = $("#id_originating_office").select2('data', '').trigger('change');
    $.getJSON(url, function(offices) {
        office_dropdown.select2({
            data: offices,
            placeholder: "Originating Office", 
            allowClear: true,
        });
        if (offices.length == 1) {
            office_dropdown.select2('val', offices[0].id);
        }
    });
    
}


function update_pr_currency(country_id) {
    var url = '/api/v1/currencies/?country=' + country_id;
    var currency_dropdown= $("#id_pr_currency").select2('data', '').trigger('change');
    $.getJSON(url, function(currencies) {
        currency_dropdown.select2({
            data: currencies,
            placeholder: "PR Currency", 
            allowClear: true,
        });
        if (currencies.length == 1) {
            currency_dropdown.select2('val', currencies[0].id);
        }
    });
    
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
