//Validates that the input string is a valid date formatted as "mm/dd/yyyy"
function isValidDate(dateString)
{
    // First check for the pattern
    if(!/^\d{1,2}\/\d{1,2}\/\d{4}$/.test(dateString))
        return false;

    // Parse the date parts to integers
    var parts = dateString.split("/");
    var day = parseInt(parts[1], 10);
    var month = parseInt(parts[0], 10);
    var year = parseInt(parts[2], 10);

    // Check the ranges of month and year
    if(year < 1000 || year > 3000 || month == 0 || month > 12)
        return false;

    var monthLength = [ 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ];

    // Adjust for leap years
    if(year % 400 == 0 || (year % 100 != 0 && year % 4 == 0))
        monthLength[1] = 29;

    // Check the range of the day
    return day > 0 && day <= monthLength[month - 1];
}	

function sign_out()
{
	window.location = $("#logout-link").attr('href');
}

function check_cancel()
{
	if ($("#tutor").val() == $("#user-email").html())
	{
		alert("You cannot tutor yourself. The student must log in to their account and then select who tutored them from the list.")
		return true;
	}
}

//Submit form.
function send()
{
	if ($("#page-member").length > 0)
		if (!window.confirm("You are also a club member. The person who was tutored is supposed to fill out this form. If you tutored someone, click cancel and have them log in instead. If you are a club member but were also tutored, click ok."))
			return false;
	
	var collectedData = '';
	var cancelMessage = "";

	$("#data > input, #data > select").each(function(index)
	{
		//Rule out the submit button...
		if ($(this).attr('id') == "submit")
			return;
		
		//Run some checks on the data to be submitted:
		if (cancelMessage!="") return;
		
		//Check if there is a required attribute, then require that it is not blank/empty.
		var req = $(this).attr('required');
		console.log($(this).attr('id') + req)
		if (typeof req !== typeof undefined && req !== false)
			if (!$(this).val() || 0 === $(this).val().length)
				{
					cancelMessage = "Please enter data for required field \"" + $(this).attr('id') + "\"";
					return;
				}
		
		//Make sure date is valid.
		if ($(this).attr('id') == "date")
			if (!isValidDate($(this).val()))
			{
				cancelMessage = "Invalid date entered (" + $(this).val() + ")";
				return;
			}
			
		var what = encodeURIComponent($(this).attr('id'));
		var value = encodeURIComponent($(this).val());
		
		collectedData = collectedData.concat('&', 'data_', what, '=', value);
	});

	//Cancel the submission.
	if (cancelMessage != "")
	{
		alert(cancelMessage);
		return;
	}

	if (check_cancel())
		return;
	
	if ($("#tutor").val() == $("#user-email").html())
		
	{
		alert();
		return;
	}
	
	$('#loader').show();
	$("#submit").prop("disabled", true);
	
	$.ajax({
		type: "POST",
		data: collectedData,
		url: "submit",
		dataType: "text",
		success: function(data) {
			console.log('Response was: ' + data);
			$('#loader').hide();
			$("#submit").prop("disabled", false);
			var title = "Thank you!";
			var message = data;
			$.modal("<div><h1>" + title + "</h1><p>" + message + "</p><input type = \"button\" value = \"Close\" class = \"simplemodal-close align-bottom-button\" style = \"left: 15px\"/><input type = \"button\" value = \"Close and Sign Out\" class = \"simplemodal-close align-bottom-button\" onclick=\"sign_out();\"  style = \"left: 115px\" /></div>");
			if (data.indexOf("error") == -1 && data.indexOf("Error") == -1)
			{
				$("#minutes, #subject, #satisfaction, #comments").val("");
			}
		}
	});

}

//Stop people from double-sending
function setDisabled(which)
{
	$("#data > input, #data > select").each(function(index)
			{
		$(this).prop("disabled", which);
			});
}

//On page load.
$(function($)
		{
	$('.date-control').datepicker({
		"setDate": new Date(),
		"autoclose": true
	});

	var today = new Date();
	var dd = today.getDate();
	var mm = today.getMonth()+1; //Jan=0
	var yyyy = today.getFullYear();

	if(dd<10) dd='0'+dd; 
	if(mm<10) mm='0'+mm;

	$("#date").val(mm+'/'+dd+'/'+yyyy);
	$("#minutes").numeric();

	$("#submit").click(send);

	
	//Retrieve tutor list
	$.ajax({
		type: 'GET',
		data: 'tutors',
		url: 'request',
		dataType: 'text',
		success: function(data)
		{
			$('#tutor').append('<option disabled selected value = "" style = "display: none;"> -- select a tutor -- </option>');
			
			JSON.parse(data).map(function(tutor)
			{
				$('#tutor').append($("<option></option>").attr("value", tutor[2]).text(tutor[0] + ', ' + tutor[1] + ', ' + tutor[2]));
			});
			
			$("#tutors-loading").remove();
		}
	});
	
	$("#tutor").change(check_cancel);
});
