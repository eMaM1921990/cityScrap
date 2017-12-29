/**
 * Created by mac on 10/20/17.
 */

$('#scrap').on('click',function(event){
    $.ajax({
        url: "/scrap/",
        type: 'POST',
        data: {
            csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
            id:$('#city').val(),
            website:$('#website').val()
        },
        success: function (responseText) {
            console.log(responseText);
        },
        error: function (xhr, errmsg, err) {
            console.log(errmsg);
        }
    });
});