var HumChart, TempChart, OccChart;
var humidityData, temperatureData, occupancyData
var DTfrom, DTto

	// Used for displaying latest readings 
	function docWrite(variable) {
	    document.write(variable);
	}

	// When the page loads MakeCharts is called
	$(document).ready(MakeCharts)
	function MakeCharts(){
		// An ajax request is sent to the current url
		$.ajax({

			url: window.location.pathname,
			// If it succeeds, all the charts & latest readings are created/upadted 
			success: function(response){


				humidityData = response["humidity_data"]
				temperatureData = response["temperature_data"]
				occupancyData = response["occupancy_data"]

				// If the user chose a time-range, filter data based on user-supplied parameters,
				// If the user did not, show data older than now() - 24 hours with no upper boundary
				filterData();

				MakeHumidityChart(humidityData, "ChartHumidity");
				MakeTemperatureChart(temperatureData, "ChartTemperature");
				MakeOccupancyChart(occupancyData, "ChartOccupancy");
				
				document.getElementById("h").innerHTML = response["latest_hum"].toPrecision(4);
				document.getElementById("t").innerHTML = response["latest_temp"].toPrecision(4);
				document.getElementById("o").innerHTML = response["latest_occ"];

			},
			// The call is repeated every minute
			complete: function(){
				//console.log("it does things");
				setTimeout(MakeCharts, 60000);
			}
			
		});
	};


	// Below follow 3 almost identical functions which create the 
	// humidity, temperature, and occupancy charts respectively.
	// These cannot be condensed into a singular function as each chart must be tied
	// to its own variable which can be destroyed whenever the chart needs to be redrawn.
	
	function MakeHumidityChart(data, canvasID){
		var ctx = document.getElementById(canvasID);

		if(typeof HumChart !== 'undefined'){
			HumChart.destroy();
		}

		HumChart = new Chart(ctx,{
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


	function MakeTemperatureChart(data, canvasID){
		var ctx = document.getElementById(canvasID);

		if(typeof TempChart !== 'undefined'){
			TempChart.destroy();
		}

		TempChart = new Chart(ctx,{
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


	function MakeOccupancyChart(data, canvasID){
		var ctx = document.getElementById(canvasID);

		if(typeof OccChart !== 'undefined'){
			OccChart.destroy();
		}
		
		OccChart = new Chart(ctx,{
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

	
	//Filter data based on 'from' & 'to' dateTime data input by the user into the dateTimePicker
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

	// Keeping this around because the whole mechanism for requesting and filtering data will have to be reworked eventually


	// function filterData(){
	// 	var newHumData = [...humidityData["labels"]];
	// 	newHumData = newHumData.filter(startEndDateFilter);

	// 	var newTempData = [...temperatureData["labels"]];
	// 	newTempData = newTempData.filter(startEndDateFilter);

	// 	var newOccData = [...occupancyData["labels"]];
	// 	newOccData = newOccData.filter(startEndDateFilter);
		
	// 	return [newHumData, newTempData, newOccData];

	// }


	// Run all humidity, temperature, and occupancy data through startEndDateFilter()
	function filterData(){
		humidityData["labels"] = humidityData["labels"].filter(startEndDateFilter);
		temperatureData["labels"] = temperatureData["labels"].filter(startEndDateFilter);
		occupancyData["labels"] = occupancyData["labels"].filter(startEndDateFilter);
		
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



