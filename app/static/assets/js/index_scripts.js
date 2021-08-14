// ==ClosureCompiler==
// @output_file_name default.js
// @compilation_level SIMPLE_OPTIMIZATIONS
// ==/ClosureCompiler==


function toggleLegend() {
    var x = document.getElementById("legend");
    if (x.style.display === "none") {

        x.style.display = "block";
    } else {
        x.style.display = "none";

    }
}




searchMarkers = function() { 

    var search_query = document.getElementById('search_markers').value;
    search_query = search_query.toUpperCase();
    // var ml = crime_map_markers.length;
    var criminal_name_found = false;
    var location_found = false;
    var is_generic = false;
    var action_taken_found = false;


    for (var j = 0; j < crime_map_markers.length; j++) {



        if (search_query.toLowerCase() == "marblehead" || search_query.length <= 3) {
            is_generic = true;
            break;
        }


        markers = crime_map_markers[j];




        if (markers.location) {

			var alt_markers = markers.location.replace("ST", "STREET").replace("RD", "ROAD").replace("AVE", "AVENUE").replace("CT", "COURT").replace("CIR", "CIRCLE").replace("DR", "DRIVE").replace("LN","LANE").replace("BLVD", "BOULEVARD").replace("CIR", "CIRCLE"); // use regex

            if (markers.location.includes(search_query) || alt_markers.includes(search_query)) {
  
                var latLng = new google.maps.LatLng(markers.lt, markers.ln);
                crime_map.panTo(latLng);
                crime_map.setZoom(17);
                markers.setAnimation(google.maps.Animation.DROP);
                location_found = true;


            }

        }

    }

    for (var k = 0; k < crime_map_markers.length; k++) {

        markers = crime_map_markers[k];

        if (markers.criminal_name) {

            if (markers.criminal_name.includes(search_query)) {

                var latLng = new google.maps.LatLng(markers.lt, markers.ln);
                crime_map.panTo(latLng);
                crime_map.setZoom(20);
                makeBounce(markers);
                criminal_name_found = true;

            }

        }

    }

    for (var l = 0; l < crime_map_markers.length; l++) {

        markers = crime_map_markers[l];

        if (markers.action_taken) {

            if (markers.action_taken.includes(search_query)) {
                // console.log('action_taken match! : %s', markers.action_taken);
                var latLng = new google.maps.LatLng(markers.lt, markers.ln);
                crime_map.panTo(latLng);
                crime_map.setZoom(17);
                makeBounce(markers);
                action_taken_found = true;

            }

        }

    }

    if (is_generic && !isValidAddress(search_query) || is_generic && location_found && !isValidAddress(search_query)) {
        alert("Please try using a less generic search term");


    } else {

    }


    if (!location_found && !is_generic && !location_found && !criminal_name_found && !action_taken_found && !isValidAddress(search_query)) {
        alert("No reports found in database. Please try generalizing your search term.");


    } else {

    }



};



function makeBounce(markers) {
    markers.setAnimation(google.maps.Animation.BOUNCE);
    setTimeout(function() {
        markers.setAnimation(null);
    }, 7500);
}

function makeDrop(markers) {
    markers.setAnimation(google.maps.Animation.DROP);
    setTimeout(function() {
        markers.setAnimation(null);
    }, 7500);
}



function success() {
    if (document.getElementById("search_markers").value === "" || document.getElementById("search_markers").value.length <= 2) {
        document.getElementById('button').disabled = true;
    } else {
        document.getElementById('button').disabled = false;
    }
}

var input = document.getElementById("search_markers");
var awesomplete = new Awesomplete(input, {
    minChars: 1,
    maxItems: 6,
    autoFirst: true
});





var criminal_names_array = [];
// var locations_array = [];
var reason_array = []; 
// let test_array_3 = [];
function test() {


    for (var i = 0; i < crime_map_markers.length; i++) {

        markers = crime_map_markers[i];

        if (markers.criminal_name) {


            name = markers.criminal_name;

            var selectLtLng = new google.maps.LatLng(markers.lt, markers.ln);

            loc = markers.location;
            // officer = markers.primary_id;
			reason = markers.reason;


            criminal_names_array.push(name + " " + selectLtLng); 


			reason_array.push(reason + " " + selectLtLng)


        }

    }

	var final_array = criminal_names_array;
	awesomplete.list = final_array;

}


document.getElementById('search_markers').addEventListener('awesomplete-selectcomplete', function() { // Do we need to stop function here??

    x = this.value;
	y = this.value;
	z = this.value;





	function getCriminal() {

		document.getElementById("button").disabled = false;


		var address = y.trim();
		var cords = x.split("(")[1];

		cords = cords.split(",");
		cords = cords.toString().replace(")", "").split(",");

		name = x.split("(")[0];
		name = name.toString()
		name = name.trim();
		// console.log(name);

		var lat = Number(cords[0]);
		var lon = Number(cords[1]);
		var thisLtLng = new google.maps.LatLng(lat, lon);

		for (var i = 0; i < crime_map_markers.length; i++){ //crime_map_markers.length

			markers = crime_map_markers[i];

			if (markers.criminal_name){

				if (markers.criminal_name.toString() == name){
					// console.log("YAYY");
					crime_map.panTo(thisLtLng);
					crime_map.setZoom(20);
					makeBounce(markers);
				}

				}
			}



	}

	crim_name = x.split("(")[0];
	crim_name = crim_name.toString()
	crim_name = crim_name.trim();

	loc = y;

	for (var i = 0; i < crime_map_markers.length; i++){
		markers = crime_map_markers[i];

		if (markers.criminal_name){



			if (crim_name == markers.criminal_name){


			
				getCriminal();
		}

		}

	}

});


