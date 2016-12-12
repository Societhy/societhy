$( document ).ready(function() {

    $( function() {
	$( "#datepicker" ).datepicker();
    } );

    cnt = 1;
    if (cnt == 1)
	$("div#stepAdvancement button#btn-prev").prop("disabled",true);

    $("div#stepAdvancement button#btn-prev").on("click", function() {
	cnt--;
	updateDisplay();
    });

    $("div#stepAdvancement button#btn-next").on("click", function() {
	cnt++;
	updateDisplay()
    });

    function updateDisplay()
    {
	if (cnt == 1)
	    $("div#stepAdvancement button#btn-prev").prop("disabled", true);
	else
	    $("div#stepAdvancement button#btn-prev").prop("disabled", false);
	if (cnt == $(".registrationDatas").length)
	    $("div#stepAdvancement button#btn-next").prop("disabled", true);
	else
	    $("div#stepAdvancement button#btn-next").prop("disabled", false);
	$(".registrationDatas").hide();
	$(".data" + cnt).show();

	if (cnt > $(".registrationDatas").length)
	    cnt = $(".registrationDatas").length - 1;

    }
    $("form #mandatoryInfo input").on("blur", function() {
	ret = 0;
	$("button#submit").prop("disabled", false);
	$("form #mandatoryInfo input").each(function (index) {
	    if ($(this).val().length == 0)
	    {
		ret = 1;
		$("button#submit").prop("disabled", true);
		$("#beforeSubmit").show();
		return;
	    }
	});
	if (ret == 0)
	    $("#beforeSubmit").hide();
    });
});
