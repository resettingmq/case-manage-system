function _toggle_query_value(match, g1, g2, g3, str) {
    if (g2 === '0') {
        return [g1, '1', g3].join('');
    }
    else {
        return [g1, '0', g3].join('');
    }
}

// 添加show_disabled button到datatables预定义buttons中
$.fn.dataTable.ext.buttons.show_disabled = {
    "text": '<i class="icon ion-home"></i>显示删除项',
    "action": function(e, dt, node, config) {
        node.toggleClass('activate');
        var url = dt.ajax.url();
        url = url.replace(
            /(show_disabled=)(0|1)(\.*)/i,
            _toggle_query_value
        );
        console.log(url);
        dt.ajax.url(url).load();
    },
    "init": function(dt, node, config) {
        // 在按钮初始化的时候在ajax url中添加query args
        dt.ajax.url(dt.ajax.url() + '?show_disabled=0');
    },
    "className": 'btn-datatables'
};

$.fn.dataTable.ext.buttons.cms_colvis = {
    extend: 'colvis',
    text: '选择显示列',
}

$(document).ready(function() {

});