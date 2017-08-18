$(document).ready(function() {
    $('#id_category').change(function() {
        console.log(this.value);
        if (this.value > 7) {
            $('#id_trademark').parents('.form-group').hide();
            console.log('done');
        }
        else {
            $('#id_trademark').parents('.form-group').show();
        }
    });
});