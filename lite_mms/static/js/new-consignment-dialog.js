$(function () {
    $("#new-consignment-dialog").dialog({
        autoOpen:false,
        open:function (event, ui) {
            var session_id = $("#delivery_session_id").val();
            $.getJSON("/delivery/ajax/customer-list?delivery_session_id=" + session_id,
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
    $("#new-consignment").click(function () {
        var id = $("#delivery_session_id").val();
        if (jQuery.type(id) == "undefined" || id == "") {
            alert("当前无记录");
            return;
        }
        $.getJSON("/delivery/ajax/customer-list?delivery_session_id=" + id,
            function (data) {
                $("#new-consignment-dialog").dialog("open");
                $("#customer").empty()
                $.each(data, function (idx, v) {
                    $("#customer").append("<option value=" + v.id + ">" + v.name + "</option>");
                });
            }).error(function (data) {
                alert(data.responseText);
            });
    });
    $(".button-close").click(function () {
        $("#new-consignment-dialog").dialog("close");
    });
});
