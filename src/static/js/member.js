tutee_filter = function(item)
{
   if ($("#tuteeselect").val() == "none")
	   return true;
   if (item.values().email.indexOf($("#tuteeselect").val()) > -1)
   {
       return true;
   }
   return false;
}

var list;

//On page load.
$(function($)
{
	var options = {valueNames: [ 'name', 'email', 'date', 'subject', 'minutes' ]};
	list = new List('logdata', options);
	
	list.filter(tutee_filter);
	
	var emails = [];
	$(".list > tr").each(function() {
		var email = $(this).children(".email").children(".mailto-link").html();
		
		if (emails.indexOf(email) == -1)
		{
			var name = $(this).children(".name").html();
			$("#tuteeselect").append($("<option></option>").attr("value", email).text(name + " (" + email + ")"));
			emails.push(email);
		}
	});
	
	$("#tuteeselect").change(function(){
		list.filter();
		list.filter(tutee_filter);
	});
	
	var minutes = 0.0;
	var count = 0;
	$(".minutes").each(function(){
		minutes += parseInt($(this).html());
		count++;
	});
	
	var hours = minutes/60.0;
	var fixed = hours.toFixed(1);
	$("#info-hours").html(fixed);
	$("#info-sessions").html(count);
	
	var names = [];
	var namecount = 0;
	$(".email").each(function(){
		var name = $(this).html();
		if (names.indexOf(name) == -1)
		{
			names.push(name);
			namecount++;
		}
	});
	
	$("#info-students").html(namecount);
});