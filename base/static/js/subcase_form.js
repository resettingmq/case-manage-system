function select_category(category_value) {
    if (category_value > 7) {
        $('#id_trademarknation').parents('.form-group').hide();
        $('#id_patternnation').parents('.form-group').show();
    }
    else {
        $('#id_trademarknation').parents('.form-group').show();
        $('#id_patternnation').parents('.form-group').hide();
    }
}

$(document).ready(function() {
    // 页面加载后根据id_cateogry的值设置trademark/pattern select input显示与否
    // $('#id_category').val($('#id_category option:first').val());
    select_category($('#id_category').val());
    $('#id_category').change(function() {
        console.log($(this).val());
        select_category($(this).val());
    });
});