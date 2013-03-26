$(function () {
    $("#new-receipt-dialog").dialog({
        autoOpen:false,
        open:function (event, ui) {
            var session_id = $("#unload_session_id").val();
            $.getJSON("/order/ajax/customer-list?unload_session_id=" + session_id,
                function (data) {
                    $("#customer").empty()
                    $.each(data, function (idx, v) {
                        $("#customer").append(
                            "<option value=" + v.id + ">" + v.name + "</option>");
                    });
                }
            );
        }
    });
    $("#new-receipt").click(function () {
        var id = $("#unload_session_id").val();
        if(jQuery.type(id)=="undefined" || id==""){
            alert("当前无记录");
            return;
        }
        $.getJSON("/order/ajax/customer-list?unload_session_id=" + id,
            function (data) {
                $("#new-receipt-dialog").dialog("open");
                $("#customer").empty()
                $.each(data, function (idx, v) {
                    $("#customer").append("<option value=" + v.id + ">" + v.name + "</option>");
                    });
            }).error(function (data) {
                alert(data.responseText);
            });
    });
    $(".button-close").click(function () {
        $("#new-receipt-dialog").dialog("close");
    });
});
