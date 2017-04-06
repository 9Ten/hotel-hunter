function showcomplete() {
    $("#first").hide();
    $("#second").show();
}

function reset() {
    $("#first").show();
    $("#second").hide();
}

$(function () {
    $(".getloader").click(function (e) {
        e.preventDefault();
        reset();
        setTimeout(showcomplete, 2000);
    });
});

