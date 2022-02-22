//
// Get the Django CSRF middleware token
//

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var charts = [ undefined, undefined, undefined ];

function MakeChart(idx, data, canvasID) {
    var ctx = document.getElementById(canvasID);

    if (charts[idx] != undefined) {
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
        // If it succeeds, all the charts & latest readings are created/updated
        success: function(response) {
            MakeChart(0, response["humidity_data"], "ChartHumidity");
            MakeChart(1, response["temperature_data"], "ChartTemperature");
            MakeChart(2, response["occupancy_data"], "ChartOccupancy");

            if (response["latest_hum"] != undefined) {
                document.getElementById("h").innerHTML = response["latest_hum"].toPrecision(4) + " %";
            }
            if (response["latest_temp"] != undefined) {
                document.getElementById("t").innerHTML = response["latest_temp"].toPrecision(4) + " C";
            }
            if (response["latest_occ"] != undefined) {
                document.getElementById("o").innerHTML = response["latest_occ"];
            }
            if (response["latest_weather"] != undefined) {
                document.getElementById("outside_h").innerHTML = response["latest_weather"].main.humidity + " %";
                document.getElementById("outside_t").innerHTML = response["latest_weather"].main.temp + " C";
            }
        },
        // The call is repeated every minute
        complete: function() {
            setTimeout(MakeCharts, 60000);
        }
    });
};

// When the page loads MakeCharts is called
$(document).ready(MakeCharts)
