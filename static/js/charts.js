// When the page loads MakeCharts is called
$(document).ready(MakeCharts)

function MakeCharts(){
	// An ajax request is sent to the current url
	$.ajax({
		url: window.location.pathname,
		// If it succeeds, all the charts & latest readings are created/upadted
		success: function(response){

			MakeHumidityChart(response["humidity_data"], "ChartHumidity");
			MakeTemperatureChart(response["temperature_data"], "ChartTemperature");
			MakeOccupancyChart(response["occupancy_data"], "ChartOccupancy");

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

var HumChart, TempChart, OccChart;

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
