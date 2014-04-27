/**
 * usdacm_caledar.js
 * Laura Londo
 * 
 * 
 * JavaScript Events calendar generator for the USD ACM website. Reads the
 * current year and month from the events page and queries the events table
 * in the database for the appropriate event data to create an HTML table
 * calendar. Allows the user to click the previous and next buttons to 
 * scroll through different months in the calendar. A new calendar table is 
 * generated on button click event.
 **/


//month name strings
var monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 
		  'August', 'September', 'October', 'November', 'December'];


//function recieves the current month and year and returns calendar HTML
//for either the next month or the previous month. The function queries
//the database for event information for the month.
var genCalendar = function() {
    //get calendar current month view information from the header
    var calendar = $('#cal-head');
    var year = calendar.attr("data-year");   //the currently shown year
    var month = calendar.attr("data-month"); //the currently shown month

    //get the previous month and year if previous was clicked
    if( this.id == "prev-month") {
	if( month == 1) { //if first month
	    month = 12;   //loop back to 12
	    year--;    //of previous year
	}
	else {
	    month--;
	}
    }

    //get the next month and year if next was clicked
    else if (this.id == "next-month"){
	if (month == 12){ //if last month
	    month = 1;    //loop back to 1
	    year++;       //of next year
	}
	else {
	    month++;      //else just next month
	}
    }

    //update calendar header with the new year and month info
    calendar.attr("data-year", year);
    calendar.attr("data-month", month);
    $('#title-year').html(year);
    $('#title-month').html(monthNames[month-1]);

    //var prevNumDays = new Date(prevYear, prevMonth, 0).getDate();
    //var currNumDays = new Date(year, month, 0).getDate();
    //var startDay = new Date(year, month, 1).getDay();

    //query the database for all event information for the new month
    //sends a GET request to the page rendered by the get_month_events view in views.py
    $.get('/get_month_events/',             //URL to send the request to
          {newYear: year, newMonth: month}, //data to send in the request
	  function(data) {                  //function to handle the response
	      var days = JSON.parse(data);  //parse JSON message from python view

	      //compose html string
	      var html = "";
	      var gridNum = 0;
	      for(var d in days) { //for each day/box on the calendar,
		  day = days[d];
		  var num = day["day"];
		  var events = day["events"];
		  if( gridNum%7 == 0){       //if this is the begining of a week,
		      html += "<tr>";        //start a new row
		  }
		  
		  html += "<td";             //a new data (column) for this row
		  //check for inactive days (belonging to prev or next month)
		  if(!day["active"]){ html += " class=\"inactive\"";}
		  html += "><div>";

		  html += ("<span class=\"day\">" + num + "</span>"); //day number

		  for (var e in events) {    //for each event on this day,
		      var event = events[e];
		      html += ("<span class=\"event green\">"  //new event module
			       + event["hour"] + ":" + event["minute"]
			       + " " + event["title"] 
			       + "</span>");
		  }

		  html += "</div></td>";      //end column for this row
		  if ( (gridNum+1)%7 == 0) {  //end row on saturday
		      html += "</tr>";
		  }	
		  gridNum++;
	      }

	      //insert html string into calendar body element on the page
	      $('#calendar_body').html(html);
	  });
} //end month function






//on document load
$(document).ready(function() {
	genCalendar();                       //render the initialcalendar on page load
	$('#prev-month').click(genCalendar); //set up click event for previous button
	$('#next-month').click(genCalendar); //set up click event for next button
    });
