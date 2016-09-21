
function search() {
    var name = $("#searchItem").val();
    var selection = $("p:contains('" + name + "'):first");
    if (selection.length !== 0) {
        if (selection.is(":hidden"))
        {
            selection.parent().parent().parent().parent().prev().click();
        }
        $('html, body').animate({
            scrollTop: selection.offset().top - 100
        }, 1000);
    } else {
        alert("didn't find anything!")
    }
    };



