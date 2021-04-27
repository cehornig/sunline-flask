function populateChart() {
  var chart = document.getElementById('chart');
  var latitude = document.getElementById('lat').value;
  var longitude = document.getElementById('long').value;
  var date = document.getElementById('date').value;
  var error = document.getElementById('error');
  var fetching = document.getElementById('fetch');
  var apiString;
  var data;
  var isToday;

  error.setAttribute('style', '');

  if (latitude == '' || longitude == '') {
    error.innerHTML = "Please fill in the latitude and longitude.";
    error.setAttribute('style', 'display:inline-block');
    return;
  }

  chart.setAttribute('style', 'visibility:hidden');
  fetching.setAttribute('style', 'display:inline-block');

  if (date == '') {
    apiString = '/api/' + latitude + '/' + longitude;
    isToday = true;
  } else {
    apiString = '/api/date/' + latitude + '/' + longitude + '/' + date;
    isToday = false;
  }

  axios.get(apiString)
   .then(function(res){
     data = res.data;

     if (data["error"] == "No timezone") {
       error.innerHTML = "Sorry, we can't find a timezone for those coordinates.<br>(And we can't render times without timezones.)";
       error.setAttribute('style', 'display:inline-block');
       fetching.setAttribute('style', '');
       return;
     } else if (data["error"] == "Invalid coordinates") {
       error.innerHTML = "Not a valid latitude and longitude.";
       error.setAttribute('style', 'display:inline-block');
       fetching.setAttribute('style', '');
       return;
     }

     renderChart(data, isToday);
     fetching.removeAttribute('style');
     chart.removeAttribute('style');
   });
 }

function renderChart(origData, isToday) {

  var data = [];
  var zeroPoints = true;
  for (var key in origData) {
    if (origData[key]['isNegative'] == "False") {
      zeroPoints = false;
      data.push(origData[key]);
    } else {
      data.push({'x': key, 'value': 'missing'});
    }
  }

  if (zeroPoints == true)
    data = [{"x": 0, "y": 0, "z": -10}];

  data['date'] = origData['date'];
  data['lat'] = origData['lat'];
  data['long'] = origData['long'];
  data['sunrise'] = origData['sunrise'];
  data['sunset'] = origData['sunset'];
  data['day_length'] = origData['day_length'];

  // Fix SunriseSunset.com returning day_length == 0 when sun is always up
  if (data["day_length"] == "0 hours, 0 minutes" && !zeroPoints)
    data["day_length"] = "24 hours, 0 minutes";

  // Also fix it listing sunrises and sunsets in both of these cases
  if (data['day_length'] == "0 hours, 0 minutes" ||
      data['day_length'] == "24 hours, 0 minutes") {
      data['sunrise'] = "N/A";
      data['sunset'] = "N/A";
     }


  var x_list = [];
  var y_list = [];
  var z_list = [];
  var time_list = [];
  var appendDate;

  if (isToday)
    appendDate = "<span style='font-size:20px'>" + origData.date + "</span><br>"
  else
    appendDate = "";

  var title =   appendDate
                + "<span style='font-size:16px'>Sunrise: "
                + data["sunrise"]
                + "</span>, <span style='font-size:16px'>Sunset: "
                + data["sunset"]
                + "</span><br><span style='font-size:16px'>Length of Day: "
                + data["day_length"]
                + "</span><br><span style='font-size:10px'>Sunrise, sunset, and day length from https://sunrise-sunset.org/api<span>";

  for (var key in data) {
    x_list.push(data[key]['x']);
    y_list.push(data[key]['y']);
    z_list.push(data[key]['z']);
    time_list.push(data[key]['timestring']);
  }
  var trace = {
    y: y_list,
    x: x_list,
    z: z_list,
    text: time_list,
    hovertemplate: '%{text}',
    mode: 'markers',
    name: '',
    line: {color: 'peru'},
    type: 'scatter3d',
    marker: {
      color: '#fcc203',
    },
  };

  var pdata = [trace];
  var layout = {
    title: title,
    font: {
      family: 'Arial',
      size: 16
    },
    scene: {
      aspectmode: 'cube',
      xaxis: {
        showgrid: false,
        tickvals: [-99, 99],
        ticktext: ['N', 'S'],
        range: [-100, 100],
        title: ""
      },
      yaxis: {
        //showticklabels: false,
        tickvals: [-99, 99],
        ticktext: ['W', 'E'],
        showgrid: false,
        title: "",
        scaleanchor: "x",
        range: [-100, 100]
      },
      zaxis: {
        showticklabels: false,
        showgrid: false,
        visible: false,
        linewidth: 0,
        title: "",
        range: [0, 100]
      },
    },
  };

  Plotly.newPlot('chart', pdata, layout);
}
