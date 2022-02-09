var charts = [ undefined, undefined, undefined ];

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
			MakeChart(0, response["humidity_data"], "ChartHumidity");
			MakeChart(1, response["temperature_data"], "ChartTemperature");
			MakeChart(2, response["occupancy_data"], "ChartOccupancy");

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
