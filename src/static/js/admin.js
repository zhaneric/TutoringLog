//On page load.
$(function($)
{
	load_lists();
	
	$('.data-view').hide();
	
	$(".view-log").click(function(){
		$('#data-title').html("Tutoring log for " + $("#club-member").val());
		$('.data-view').not('#table-view').hide();
		$('#table-view').show();
		
		if ($(this).attr('data-which') == 'club-member')
		{
			loadTutor($("#club-member").val())
		}
	});
	
	$('#show-none-month').click(function()
	{
		$('#data-title').html("Club members who haven't tutored in 30 days");
		$('.data-view').not('#stat-view').hide();
		$('#stat-view').show();
		$('#stat-view').html(statistics['none_month'].join(', '));
	});
	
	$(".download-excel").click(function(){
		window.open('/request?data=tutor&email=' + encodeURIComponent($("#club-member").val()) + '&type=csv', '_blank');
	});
	
	$(".printable-report").click(function(){
		window.open('/request?data=tutor&email=' + encodeURIComponent($("#club-member").val()) + '&type=pdf', '_blank');
	});
});

var statistics = null;

function load_lists()
{
	//Retrieve TUTOR list
	$.ajax({
		type: 'GET',
		data: 'tutors',
		url: 'request',
		dataType: 'text',
		success: function(data)
		{
			$('#club-member').append('<option disabled selected value = "" style = "display: none;"> -- select a tutor -- </option>');
			
			JSON.parse(data).map(function(tutor)
			{
				$('#club-member').append($("<option></option>").attr("value", tutor[2]).text(tutor[0] + ', ' + tutor[1] + ', ' + tutor[2]));
			});
			
			$("#tutors-loading").remove();
		}
	});
	
	//Retrieve TUTEE list
	$.ajax({
		type: 'GET',
		data: 'tutees',
		url: 'request',
		dataType: 'text',
		success: function(data)
		{
			$('#student').append('<option disabled selected value = "" style = "display: none;"> -- select a tutee -- </option>');
			
			JSON.parse(data).map(function(tutor)
			{
				$('#student').append($("<option></option>").attr("value", tutor[1]).text(tutor[0] + ', ' + tutor[1]));
			});
			
			$("#students-loading").remove();
		}
	});
	
	//Retrieve STATISTICS
	$.ajax({
		type: 'GET',
		data: 'statistics',
		url: 'request',
		dataType: 'text',
		success: function(data)
		{
			statistics = JSON.parse(data);
			
			$('#stat-members').html(statistics['members']);
			$('#stat-tutees').html(statistics['tutees']);
			$('#stat-time').html(format_minutes(parseInt(statistics['minutes'])));
			$('#stat-sessions').html(statistics['sessions']);
			$('#stat-yesterday').html(statistics['yesterday']);
			$('#stat-week').html(statistics['week']);
			$('#stat-none-month').prepend(String(statistics['none_month'].length));
			$('#stat-top').html(statistics['top_tutor'][0] + ' (' + format_minutes(parseInt(statistics['top_tutor'][2])) + ')');
		}
	});
}

function loadTutor(email)
{
	$('#data-table').empty();
	$.ajax({
		type: "GET",
		data: {'data': 'tutor', 'email': email},
		url: "request",
		dataType: "text",
		success: function(data) {
			$('#data-table').append('<thead><tr><td><input type = "checkbox" id = "data-select-all" /></td><td>Tutee Name</td><td>Tutee Email</td><td>Subject</td><td>Date</td><td>Minutes</td><td>Satisfaction</td><td>Comments</td><td>Session ID</td></tr></thead>');
			var parsed = JSON.parse(data);
			//var keys = ["tutee_name", "tutee_email", "subject", "date_tutored", "minutes", "satisfaction", "comments", "id"];
			var keys = [3, 4, 8, 6, 7, 9, 10, 11];
			var body = $('<tbody></tbody>');
			var total_minutes = 0;
			for (var i = 0; i < parsed.length; i++)
			{
				var row = $('<tr></tr>');
				row.append($('<td></td>').attr('class', 'data-select').append('<input type = "checkbox" data-id = "' + parsed[i][11] + '" />'))
				var j;
				for (j = 0; j < keys.length; j++)
				{
				    var key = keys[j];
				    var content = null;
				    if (key == 10)
				    	content = '<div style="max-width: 180px; max-height: 80px; overflow: auto;">' + parsed[i][key] + '</div>';
					else
						content = parsed[i][key];
				    
				    if (key == 7)
				    	total_minutes += parseInt(parsed[i][key]);
				    
				    row.append($('<td></td>').attr('class', 'data-' + key).html(content));
				}
				body.append(row);
			}
			$('#data-table').append(body);
			
			$('#data-time').html(format_minutes(total_minutes))
		}
	});
}

function format_minutes(time)
{
	hours = Math.floor(time/60);
    minutes = time % 60;
    return String(hours) + (hours > 0 ? (hours > 1 ? ' hours' : ' hour') : '') + ' ' + String(minutes) + (minutes > 0 ? (minutes > 1 ? ' minutes' : ' minute') : '');
}