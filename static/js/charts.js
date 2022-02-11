var charts = [ undefined, undefined, undefined ];
var DTfrom, DTto;

function MakeChart(idx, data, canvasID) {
	var ctx = document.getElementById(canvasID);

	if(charts[idx] != undefined) {
		charts[idx].destroy();
	}

	charts[idx] = new Chart(ctx, {
		type: 'line',
		data: data,
		options: {
			plugins: {
				legend: {
					labels: {
						color: "#F7F9F9",
						font: {
							size: 12
						}
					}
				}
			},
			scales: {
				y: {
					ticks: {
						color: "#F7F9F9",
					}
				},
				x: {
					ticks: {
						color: "#F7F9F9",
					}
				},
			}
		}
	});
}

function MakeCharts() {
	// An ajax request is sent to the current url
	$.ajax({
		url: "/filter/latest/",
		data: jQuery.param({ location: document.getElementById("location_select").value }),
		// If it succeeds, all the charts & latest readings are created/upadted
		success: function(response) {

			humidityData = response["humidity_data"];
			temperatureData = response["temperature_data"];
			occupancyData = response["occupancy_data"];

			filterData();

			MakeChart(0, humidityData, "ChartHumidity");
			MakeChart(1, temperatureData, "ChartTemperature");
			MakeChart(2, occupancyData, "ChartOccupancy");

			if (response["latest_hum"] != undefined) {
				document.getElementById("h").innerHTML = response["latest_hum"].toPrecision(4);
			}
			if (response["latest_temp"] != undefined) {
				document.getElementById("t").innerHTML = response["latest_temp"].toPrecision(4);
			}
			if (response["latest_occ"] != undefined) {
				document.getElementById("o").innerHTML = response["latest_occ"];
			}
			if (response["latest_weather"] != undefined) {
				document.getElementById("outside_h").innerHTML = response["latest_weather"].main.temp;
				document.getElementById("outside_t").innerHTML = response["latest_weather"].main.humidity;
			}
		},
		// The call is repeated every minute
		complete: function(){
			//console.log("it does things");
			setTimeout(MakeCharts, 60000);
		}
	});
};

// When the page loads MakeCharts is called
$(document).ready(MakeCharts)


function startEndDateFilter(arr){

		yesterday = moment().subtract(1, 'days').format('MM-DD-YYYY H:mm:ss');
		// (Default) if the user provided none, keep everything gathered after now()-24h
		if(DTfrom == null && DTto == null){
			return (arr >= yesterday);

		}
		// If only 'to' provided, keep everything gathered before 'to'
		else if(DTfrom == null && DTto != null){
			return (arr <= DTto);

		}
		// If only 'from' proided, keep everything gathered after 'from'
		else if(DTfrom != null && DTto == null){
			return (arr >= DTfrom);
		}
		// If both values provided, keep everything gathered between 'from' & 'to'
		else {
			return (arr >= DTfrom && arr <= DTto);
		}

	}

	// Run all humidity, temperature, and occupancy data through startEndDateFilter()
	function filterData(){
		humidityData["labels"] = humidityData["labels"].filter(startEndDateFilter);
		temperatureData["labels"] = temperatureData["labels"].filter(startEndDateFilter);
		occupancyData["labels"] = occupancyData["labels"].filter(startEndDateFilter);
		console.log(humidityData);
		
		//return [newHumData, newTempData, newOccData];

	}

	// Tempus Dominus (chosen dateTime picker) function provided by official documentation at:
	// https://getdatepicker.com/5-4/Usage/#setting-options
	// Modified to set values based on which all data fitration takes place
	$(function DateTimeRange() {
	    $('#dateTimeFrom').datetimepicker({
	    	useCurrent: false,
	    	defaultDate: moment().subtract(1, 'days'),
	    });
	    $('#dateTimeTo').datetimepicker({
	        useCurrent: false,
	    	//defaultDate: moment(),

	    });
	    $("#dateTimeFrom").on("change.datetimepicker", function (e) {
	        $('#dateTimeTo').datetimepicker('minDate', e.date);
	        DTfrom = moment(e.date._d).format('MM-DD-YYYY H:mm:ss');
	        console.log(DTfrom);
	    });
	    $("#dateTimeTo").on("change.datetimepicker", function (e) {
	        $('#dateTimeFrom').datetimepicker('maxDate', e.date);
	        DTto = moment(e.date._d).format('MM-DD-YYYY H:mm:ss');
	        console.log(DTto);
	    });
	});