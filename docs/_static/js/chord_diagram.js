function chord_diagram(matrix, tag, colors, Names, caption, size_w = 700, size_h=700)
{
	var	opacityDefault = 0.8;
	var margin = {left:20, top:20, right:20, bottom:20},
	width = Math.min(window.innerWidth, size_w) - margin.left - margin.right,
    height = Math.min(window.innerWidth, size_h) - margin.top - margin.bottom,
    innerRadius = Math.min(width, height) * .39,
    outerRadius = innerRadius * 1.1;
////////////////////////////////////////////////////////////
/////////// Create scale and layout functions //////////////
////////////////////////////////////////////////////////////
	var colors = d3.scale.ordinal()
		.domain(d3.range(Names.length))
		.range(colors);

	//A "custom" d3 chord function that automatically sorts the order of the chords in such a manner to reduce overlap	
	var chord = customChordLayout()
		.padding(.15)
		.sortChords(d3.descending) //which chord should be shown on top when chords cross. Now the biggest chord is at the bottom
		.matrix(matrix);
			
	var arc = d3.svg.arc()
		.innerRadius(innerRadius*1.01)
		.outerRadius(outerRadius);

	var path = d3.svg.chord()
		.radius(innerRadius);
		
	////////////////////////////////////////////////////////////
	////////////////////// Create SVG //////////////////////////
	////////////////////////////////////////////////////////////
		
	//var svg = d3.select("#chart").append("svg")
	var svg = d3.select(tag).append("svg")
		.attr("width", width + margin.left + margin.right)
		.attr("height", height + margin.top + margin.bottom)
		.append("g")
		.attr("transform", "translate(" + (width/2 + margin.left) + "," + (height/2 + margin.top) + ")");
		
	////////////////////////////////////////////////////////////
	////////////////////// Append Caption //////////////////////////
	////////////////////////////////////////////////////////////
		
	svg.append("text")
		.attr("class", "titles")	
		.attr("startOffset","50%")
		.style("text-anchor","middle")
		.attr({"x": 0, "y": height/2})
		.text(caption);

	////////////////////////////////////////////////////////////
	/////////////// Create the gradient fills //////////////////
	////////////////////////////////////////////////////////////

	//Function to create the id for each chord gradient
	function getGradID(d){ return "linkGrad-" + d.source.index + "-" + d.target.index; }

	//Create the gradients definitions for each chord
	var grads = svg.append("defs").selectAll("linearGradient")
		.data(chord.chords())
	   .enter().append("linearGradient")
		.attr("id", getGradID)
		.attr("gradientUnits", "userSpaceOnUse")
		.attr("x1", function(d,i) { return innerRadius * Math.cos((d.source.endAngle-d.source.startAngle)/2 + d.source.startAngle - Math.PI/2); })
		.attr("y1", function(d,i) { return innerRadius * Math.sin((d.source.endAngle-d.source.startAngle)/2 + d.source.startAngle - Math.PI/2); })
		.attr("x2", function(d,i) { return innerRadius * Math.cos((d.target.endAngle-d.target.startAngle)/2 + d.target.startAngle - Math.PI/2); })
		.attr("y2", function(d,i) { return innerRadius * Math.sin((d.target.endAngle-d.target.startAngle)/2 + d.target.startAngle - Math.PI/2); })

	//Set the starting color (at 0%)
	grads.append("stop")
		.attr("offset", "0%")
		.attr("stop-color", function(d){ return colors(d.source.index); });

	//Set the ending color (at 100%)
	grads.append("stop")
		.attr("offset", "100%")
		.attr("stop-color", function(d){ return colors(d.target.index); });
			
	////////////////////////////////////////////////////////////
	////////////////// Draw outer Arcs /////////////////////////
	////////////////////////////////////////////////////////////

	var outerArcs = svg.selectAll("g.group")
		.data(chord.groups)
		.enter().append("g")
		.attr("class", "group")
		.on("mouseover", fade(.1))
		.on("mouseout", fade(opacityDefault));

	outerArcs.append("path")
		.style("fill", function(d) { return colors(d.index); })
		.attr("d", arc)
		.each(function(d,i) {
			//Search pattern for everything between the start and the first capital L
			var firstArcSection = /(^.+?)L/; 	

			//Grab everything up to the first Line statement
			var newArc = firstArcSection.exec( d3.select(this).attr("d") )[1];
			//Replace all the comma's so that IE can handle it
			newArc = newArc.replace(/,/g , " ");
			
			//If the end angle lies beyond a quarter of a circle (90 degrees or pi/2) 
			//flip the end and start position
			if (d.endAngle > 90*Math.PI/180 & d.startAngle < 270*Math.PI/180) {
				var startLoc 	= /M(.*?)A/,		//Everything between the first capital M and first capital A
					middleLoc 	= /A(.*?)0 0 1/,	//Everything between the first capital A and 0 0 1
					endLoc 		= /0 0 1 (.*?)$/;	//Everything between the first 0 0 1 and the end of the string (denoted by $)
				//Flip the direction of the arc by switching the start en end point (and sweep flag)
				//of those elements that are below the horizontal line
				var newStart = endLoc.exec( newArc )[1];
				var newEnd = startLoc.exec( newArc )[1];
				var middleSec = middleLoc.exec( newArc )[1];
				
				//Build up the new arc notation, set the sweep-flag to 0
				newArc = "M" + newStart + "A" + middleSec + "0 0 0 " + newEnd;
			}//if
			
			//Create a new invisible arc that the text can flow along
			svg.append("path")
				.attr("class", "hiddenArcs")
				.attr("id", "arc"+i+tag+caption)
				.attr("d", newArc)
				.style("fill", "none");
		});

	////////////////////////////////////////////////////////////
	////////////////// Append Names ////////////////////////////
	////////////////////////////////////////////////////////////

	//Append the label names on the outside
	outerArcs.append("text")
		.attr("class", "titles")
		.attr("dy", function(d,i) { return (d.endAngle > 90*Math.PI/180 & d.startAngle < 270*Math.PI/180 ? 25 : -16); })
	   .append("textPath")
		.attr("startOffset","50%")
		.style("text-anchor","middle")
		.attr("xlink:href",function(d,i){return "#arc"+i+tag+caption;})
		.text(function(d,i){ return Names[i]; });
	
		
	////////////////////////////////////////////////////////////
	////////////////// Draw inner chords ///////////////////////
	////////////////////////////////////////////////////////////
	  
	svg.selectAll("path.chord")
		.data(chord.chords)
		.enter().append("path")
		.attr("class", "chord")
		.style("fill", function(d){ return "url(#" + getGradID(d) + ")"; })
		.style("opacity", opacityDefault)
		.attr("d", path)
		.on("mouseover", mouseoverChord)
		.on("mouseout", mouseoutChord);

	////////////////////////////////////////////////////////////
	////////////////// Extra Functions /////////////////////////
	////////////////////////////////////////////////////////////

	//Returns an event handler for fading a given chord group.
	function fade(opacity) {
	  return function(d,i) {
		svg.selectAll("path.chord")
			.filter(function(d) { return d.source.index !== i && d.target.index !== i; })
			.transition()
			.style("opacity", opacity);
	  };
	}//fade

	//Highlight hovered over chord
	function mouseoverChord(d,i) {
	  
		//Decrease opacity to all
		svg.selectAll("path.chord")
			.transition()
			.style("opacity", 0.1);
		//Show hovered over chord with full opacity
		d3.select(this)
			.transition()
			.style("opacity", 1);
	  
		//Define and show the tooltip over the mouse location
		$(this).popover({
			placement: 'auto top',
			container: 'body',
			mouseOffset: 10,
			followMouse: true,
			trigger: 'hover',
			html : true,
			content: function() { 
				return "<p style='font-size: 11px; text-align: center;'><span style='font-weight:900'>" + Names[d.source.index] + 
					   "</span> and <span style='font-weight:900'>" + Names[d.target.index] + 
					   "</span> are used next to each other <span style='font-weight:900'>" + d.source.value + "</span> times </p>"; }
		});
		$(this).popover('show');
	}//mouseoverChord

	//Bring all chords back to default opacity
	function mouseoutChord(d) {
		//Hide the tooltip
		$('.popover').each(function() {
			$(this).remove();
		}); 
		//Set opacity back to default for all
		svg.selectAll("path.chord")
			.transition()
			.style("opacity", opacityDefault);
	}//function mouseoutChord
}
var intervals = ["P 1","m 2","M 2","m 3","M 3","P 4","d 5","P 5","m 6","M 6","m 7","M 7"];		   
var pallete=["#ff0000","#ff7f00","#ffff00","#80ff00","#00ff00","#00ff80","#00ffff","#0080ff","#0000ff","#8000ff","#ff00ff","#ff007f"];

var data = [
  [527085.0, 33607.0, 51250.0, 21328.0, 23744.0, 41820.0, 5801.0, 28955.0, 17958.0, 29117.0, 59916.0, 52281.0, ],
  [47391.0, 21615.0, 86151.0, 9979.0, 19277.0, 8204.0, 4521.0, 20649.0, 5977.0, 34196.0, 7570.0, 77687.0, ],
  [44806.0, 81393.0, 88340.0, 17450.0, 5341.0, 19079.0, 2296.0, 9977.0, 30435.0, 25772.0, 114067.0, 3048.0, ],
  [21267.0, 3576.0, 14225.0, 13278.0, 15502.0, 29972.0, 7493.0, 9557.0, 2636.0, 44776.0, 22707.0, 20416.0, ],
  [16173.0, 17237.0, 4127.0, 33794.0, 2703.0, 13690.0, 3515.0, 5916.0, 42059.0, 2708.0, 19528.0, 2802.0, ],
  [54495.0, 3555.0, 26018.0, 15783.0, 32445.0, 20383.0, 4515.0, 59318.0, 7968.0, 16074.0, 21608.0, 20060.0, ],
  [5416.0, 6259.0, 3064.0, 7509.0, 2221.0, 2789.0, 11462.0, 2451.0, 3592.0, 5469.0, 2610.0, 3741.0, ],
  [32394.0, 9330.0, 14547.0, 11696.0, 10867.0, 56365.0, 1984.0, 10367.0, 10487.0, 25245.0, 15361.0, 4572.0, ],
  [22108.0, 4694.0, 20053.0, 3104.0, 37747.0, 14635.0, 3049.0, 21521.0, 2375.0, 19134.0, 6221.0, 14633.0, ],
  [23163.0, 22411.0, 18305.0, 52042.0, 2590.0, 17059.0, 5750.0, 10611.0, 35790.0, 16056.0, 20482.0, 5428.0, ],
  [50148.0, 3644.0, 119602.0, 13661.0, 18013.0, 15816.0, 3429.0, 18150.0, 3499.0, 23684.0, 112955.0, 116702.0, ],
  [32877.0, 111716.0, 3454.0, 22397.0, 2788.0, 9637.0, 3982.0, 3191.0, 20085.0, 5000.0, 109935.0, 14926.0, ],
];
chord_diagram(data, "#Melodic_chord_diagram", pallete, intervals, "Entire Dataset");

var data = [
	  [136644.0, 8924.0, 11029.0, 3499.0, 4582.0, 10318.0, 895.0, 5722.0, 3092.0, 6208.0, 12229.0, 11043.0, ],
	  [11386.0, 5784.0, 14463.0, 1722.0, 3446.0, 2077.0, 663.0, 4097.0, 1082.0, 5502.0, 1733.0, 14070.0, ],
	  [9403.0, 14099.0, 15241.0, 2514.0, 652.0, 3141.0, 160.0, 1174.0, 4845.0, 4275.0, 20499.0, 575.0, ],
	  [4461.0, 635.0, 1935.0, 1846.0, 2121.0, 5684.0, 1053.0, 1358.0, 278.0, 7090.0, 5345.0, 3873.0, ],
	  [2983.0, 4006.0, 292.0, 6615.0, 244.0, 1521.0, 254.0, 628.0, 6314.0, 263.0, 4031.0, 327.0, ],
	  [10996.0, 608.0, 3534.0, 1927.0, 5689.0, 3769.0, 569.0, 9423.0, 959.0, 2802.0, 3129.0, 3826.0, ],
	  [906.0, 1237.0, 350.0, 1103.0, 161.0, 321.0, 1044.0, 277.0, 254.0, 693.0, 274.0, 849.0, ],
	  [6651.0, 1518.0, 2439.0, 1285.0, 1827.0, 9103.0, 209.0, 1498.0, 1183.0, 4837.0, 2234.0, 607.0, ],
	  [4992.0, 824.0, 3913.0, 417.0, 4532.0, 3463.0, 328.0, 4499.0, 273.0, 2949.0, 999.0, 2920.0, ],
	  [4939.0, 5617.0, 3096.0, 7627.0, 326.0, 2669.0, 789.0, 1273.0, 7566.0, 2644.0, 4833.0, 885.0, ],
	  [12617.0, 829.0, 19730.0, 2267.0, 3481.0, 3308.0, 601.0, 2857.0, 447.0, 4029.0, 22414.0, 23560.0, ],
	  [8216.0, 21948.0, 537.0, 4852.0, 411.0, 1900.0, 902.0, 570.0, 3820.0, 963.0, 18415.0, 3185.0, ],
	];
	chord_diagram(data, "#Melodic_chord_diagram", pallete, intervals, "Mozart");
	var data = [
	  [44503.0, 5982.0, 12248.0, 3160.0, 2910.0, 11530.0, 983.0, 4679.0, 2772.0, 5220.0, 17729.0, 14592.0, ],
	  [11940.0, 2910.0, 33884.0, 2512.0, 5195.0, 3291.0, 1821.0, 6635.0, 1771.0, 12286.0, 2419.0, 22792.0, ],
	  [12700.0, 36422.0, 33759.0, 5718.0, 1334.0, 10290.0, 896.0, 3094.0, 10962.0, 9560.0, 31181.0, 654.0, ],
	  [3354.0, 1081.0, 4140.0, 3084.0, 3111.0, 6620.0, 2029.0, 1643.0, 583.0, 5579.0, 5977.0, 7769.0, ],
	  [1879.0, 5590.0, 1061.0, 5249.0, 520.0, 4351.0, 577.0, 1094.0, 4324.0, 411.0, 5520.0, 782.0, ],
	  [14978.0, 1039.0, 9752.0, 3670.0, 5597.0, 7789.0, 1191.0, 8283.0, 2239.0, 4823.0, 8187.0, 7366.0, ],
	  [892.0, 2504.0, 662.0, 1775.0, 406.0, 892.0, 1619.0, 413.0, 848.0, 878.0, 976.0, 1278.0, ],
	  [5422.0, 3332.0, 4880.0, 1950.0, 1659.0, 8599.0, 240.0, 1981.0, 1798.0, 3254.0, 4369.0, 1295.0, ],
	  [4230.0, 1417.0, 7043.0, 554.0, 4780.0, 6456.0, 886.0, 3209.0, 634.0, 5007.0, 1387.0, 4405.0, ],
	  [4076.0, 9123.0, 8140.0, 7198.0, 366.0, 6595.0, 1184.0, 2063.0, 7069.0, 3707.0, 5362.0, 1620.0, ],
	  [15017.0, 819.0, 39656.0, 4016.0, 4660.0, 5229.0, 768.0, 4937.0, 976.0, 4730.0, 42451.0, 45888.0, ],
	  [7183.0, 37260.0, 1272.0, 6067.0, 776.0, 3764.0, 907.0, 667.0, 6031.0, 978.0, 43578.0, 2992.0, ],
	];
	
	chord_diagram(data, "#Melodic_chord_diagram", pallete, intervals, "Bach");
	var data = [
	  [95933.0, 5931.0, 6670.0, 3103.0, 3509.0, 7704.0, 806.0, 4993.0, 2684.0, 4463.0, 7534.0, 7366.0, ],
	  [7551.0, 3455.0, 7739.0, 1077.0, 1793.0, 1009.0, 478.0, 2452.0, 597.0, 3060.0, 856.0, 8063.0, ],
	  [5700.0, 8217.0, 7714.0, 1292.0, 434.0, 1463.0, 172.0, 767.0, 1975.0, 2319.0, 9639.0, 335.0, ],
	  [4022.0, 490.0, 1579.0, 1968.0, 1677.0, 2943.0, 806.0, 1118.0, 241.0, 5582.0, 2365.0, 1649.0, ],
	  [2941.0, 2542.0, 220.0, 3671.0, 265.0, 1266.0, 287.0, 514.0, 5341.0, 257.0, 1625.0, 214.0, ],
	  [7902.0, 276.0, 1860.0, 1629.0, 3094.0, 2282.0, 366.0, 7360.0, 833.0, 1782.0, 1563.0, 1665.0, ],
	  [905.0, 786.0, 221.0, 807.0, 77.0, 207.0, 1095.0, 230.0, 321.0, 778.0, 170.0, 454.0, ],
	  [5713.0, 984.0, 1214.0, 1216.0, 1466.0, 7514.0, 126.0, 1002.0, 905.0, 3325.0, 1361.0, 386.0, ],
	  [3809.0, 581.0, 1736.0, 224.0, 4479.0, 1782.0, 237.0, 3328.0, 207.0, 1614.0, 765.0, 1347.0, ],
	  [4040.0, 2629.0, 1671.0, 6218.0, 260.0, 1669.0, 871.0, 1192.0, 4571.0, 2119.0, 2322.0, 765.0, ],
	  [7176.0, 472.0, 9044.0, 982.0, 1765.0, 1778.0, 367.0, 1832.0, 310.0, 2540.0, 10208.0, 10914.0, ],
	  [5002.0, 11765.0, 354.0, 2250.0, 315.0, 1023.0, 437.0, 421.0, 2129.0, 483.0, 8979.0, 1536.0, ],
	];
	chord_diagram(data, "#Melodic_chord_diagram", pallete, intervals, "Beethoven");
	
	var data = [
	  [337511.0, 12876.0, 35520.0, 51816.0, 43589.0, 49628.0, 12369.0, 42225.0, 31588.0, 29518.0, 27056.0, 11916.0, ],
	  [12160.0, 8435.0, 7939.0, 22442.0, 11220.0, 8944.0, 3701.0, 4706.0, 4757.0, 4223.0, 2580.0, 1534.0, ],
	  [34043.0, 6965.0, 47096.0, 51287.0, 41849.0, 28622.0, 8585.0, 17540.0, 11238.0, 12418.0, 6435.0, 2293.0, ],
	  [53530.0, 25026.0, 49148.0, 186041.0, 85168.0, 68838.0, 26731.0, 52012.0, 28863.0, 26293.0, 12374.0, 2538.0, ],
	  [47321.0, 10268.0, 44862.0, 87399.0, 117751.0, 66368.0, 24249.0, 42412.0, 17410.0, 34400.0, 6967.0, 3274.0, ],
	  [55179.0, 8925.0, 28461.0, 72115.0, 65975.0, 85981.0, 19094.0, 53737.0, 34641.0, 27119.0, 7853.0, 2132.0, ],
	  [10789.0, 3597.0, 7490.0, 25808.0, 22485.0, 17344.0, 22291.0, 13191.0, 12628.0, 15616.0, 6397.0, 1576.0, ],
	  [43954.0, 4156.0, 18811.0, 50874.0, 41166.0, 57827.0, 14875.0, 51813.0, 27816.0, 36890.0, 11673.0, 3401.0, ],
	  [36158.0, 4937.0, 9748.0, 29157.0, 17496.0, 32458.0, 14176.0, 31170.0, 31183.0, 21884.0, 13385.0, 1699.0, ],
	  [32457.0, 3657.0, 12223.0, 25462.0, 29852.0, 27101.0, 14350.0, 38100.0, 22079.0, 38481.0, 14527.0, 7863.0, ],
	  [19340.0, 2637.0, 6184.0, 12135.0, 9093.0, 7135.0, 6451.0, 11398.0, 15310.0, 16068.0, 10254.0, 1318.0, ],
	  [10883.0, 1391.0, 2427.0, 2758.0, 2925.0, 2305.0, 1382.0, 3061.0, 1978.0, 8179.0, 1312.0, 2095.0, ],
	];
	
	chord_diagram(data, "#Harmonic_chord_diagram", pallete, intervals, "Entire Dataset");
	
	var data = [
	  [99476.0, 3197.0, 8329.0, 12519.0, 10084.0, 11806.0, 2496.0, 8189.0, 7425.0, 5615.0, 5086.0, 2614.0, ],
	  [3051.0, 909.0, 1223.0, 3429.0, 1767.0, 1265.0, 624.0, 609.0, 740.0, 687.0, 338.0, 209.0, ],
	  [7432.0, 1138.0, 8260.0, 9311.0, 7504.0, 4970.0, 1131.0, 2660.0, 2174.0, 1741.0, 758.0, 355.0, ],
	  [12460.0, 3593.0, 8341.0, 41055.0, 19045.0, 11562.0, 4580.0, 9068.0, 4709.0, 3919.0, 2351.0, 328.0, ],
	  [10413.0, 1585.0, 7629.0, 18681.0, 24384.0, 12309.0, 3532.0, 6978.0, 3125.0, 5754.0, 1035.0, 543.0, ],
	  [12767.0, 1375.0, 4656.0, 11955.0, 12235.0, 18164.0, 2826.0, 8362.0, 6129.0, 4124.0, 1048.0, 352.0, ],
	  [2149.0, 479.0, 1046.0, 4413.0, 3871.0, 2577.0, 4382.0, 2003.0, 2725.0, 2464.0, 956.0, 288.0, ],
	  [8584.0, 706.0, 3033.0, 8178.0, 7112.0, 9409.0, 2562.0, 10149.0, 3988.0, 5410.0, 1349.0, 388.0, ],
	  [8328.0, 782.0, 1905.0, 4967.0, 3157.0, 6161.0, 1922.0, 4785.0, 6792.0, 3462.0, 1900.0, 236.0, ],
	  [5829.0, 582.0, 1909.0, 4040.0, 4805.0, 4410.0, 2224.0, 6104.0, 3833.0, 8646.0, 2260.0, 1415.0, ],
	  [3854.0, 352.0, 691.0, 2072.0, 1623.0, 1014.0, 846.0, 1590.0, 2466.0, 2571.0, 2105.0, 197.0, ],
	  [2509.0, 159.0, 418.0, 363.0, 399.0, 352.0, 227.0, 365.0, 268.0, 1667.0, 196.0, 365.0, ],
	];
	chord_diagram(data, "#Harmonic_chord_diagram", pallete, intervals, "Mozart");
	var data = [
	  [42916.0, 2464.0, 6621.0, 10161.0, 7527.0, 7035.0, 1857.0, 9568.0, 5227.0, 6068.0, 7815.0, 2650.0, ],
	  [2491.0, 872.0, 1587.0, 7196.0, 2952.0, 2506.0, 876.0, 1489.0, 1239.0, 1240.0, 590.0, 277.0, ],
	  [6192.0, 1588.0, 4202.0, 16178.0, 12503.0, 7297.0, 2162.0, 4767.0, 2927.0, 3413.0, 1458.0, 416.0, ],
	  [10106.0, 8530.0, 15859.0, 29598.0, 22708.0, 23050.0, 6344.0, 14641.0, 8521.0, 7301.0, 3320.0, 507.0, ],
	  [8740.0, 2589.0, 14206.0, 20690.0, 15206.0, 20320.0, 8258.0, 11686.0, 4052.0, 8827.0, 1655.0, 898.0, ],
	  [8138.0, 2465.0, 6762.0, 23918.0, 19393.0, 12546.0, 6765.0, 18593.0, 7496.0, 7663.0, 2166.0, 335.0, ],
	  [1387.0, 861.0, 1558.0, 7464.0, 7980.0, 6793.0, 2191.0, 4293.0, 5140.0, 4875.0, 1566.0, 230.0, ],
	  [9210.0, 1021.0, 4882.0, 15198.0, 12321.0, 19059.0, 4646.0, 8288.0, 10440.0, 13537.0, 3838.0, 848.0, ],
	  [6074.0, 1160.0, 2215.0, 8214.0, 3989.0, 6758.0, 5773.0, 12280.0, 4425.0, 7481.0, 5474.0, 308.0, ],
	  [7841.0, 876.0, 3395.0, 7053.0, 8070.0, 7902.0, 3650.0, 12485.0, 8623.0, 9752.0, 5556.0, 2606.0, ],
	  [4562.0, 664.0, 1407.0, 4020.0, 3808.0, 2288.0, 1588.0, 4120.0, 5541.0, 5516.0, 1344.0, 177.0, ],
	  [2318.0, 252.0, 468.0, 792.0, 781.0, 518.0, 229.0, 1052.0, 481.0, 2113.0, 252.0, 190.0, ],
	];
	chord_diagram(data, "#Harmonic_chord_diagram", pallete, intervals, "Bach");
	var data = [
	  [44963.0, 1855.0, 5187.0, 8056.0, 6275.0, 8725.0, 1590.0, 6175.0, 5346.0, 3676.0, 3185.0, 1415.0, ],
	  [1739.0, 1351.0, 764.0, 1760.0, 1056.0, 913.0, 253.0, 438.0, 577.0, 373.0, 261.0, 253.0, ],
	  [4727.0, 631.0, 6506.0, 5034.0, 4015.0, 3165.0, 778.0, 1630.0, 1374.0, 1159.0, 735.0, 226.0, ],
	  [7780.0, 1977.0, 4811.0, 29344.0, 10201.0, 6121.0, 2427.0, 6123.0, 2854.0, 3010.0, 1376.0, 314.0, ],
	  [6560.0, 921.0, 3786.0, 9717.0, 18700.0, 6845.0, 2345.0, 4306.0, 2374.0, 3459.0, 761.0, 281.0, ],
	  [8776.0, 873.0, 3166.0, 6636.0, 6190.0, 12211.0, 1879.0, 4948.0, 4916.0, 2503.0, 767.0, 192.0, ],
	  [1592.0, 310.0, 612.0, 2359.0, 2356.0, 1704.0, 3396.0, 1290.0, 1677.0, 1637.0, 686.0, 105.0, ],
	  [6281.0, 506.0, 1927.0, 5753.0, 4408.0, 5123.0, 1533.0, 7488.0, 2739.0, 2925.0, 1215.0, 337.0, ],
	  [5989.0, 527.0, 1189.0, 3095.0, 2468.0, 4680.0, 1204.0, 3218.0, 5256.0, 2161.0, 1016.0, 218.0, ],
	  [3925.0, 326.0, 1205.0, 2839.0, 3247.0, 2693.0, 1542.0, 3173.0, 2311.0, 4415.0, 1285.0, 676.0, ],
	  [2594.0, 245.0, 612.0, 1480.0, 842.0, 653.0, 632.0, 1181.0, 1361.0, 1665.0, 1487.0, 156.0, ],
	  [1525.0, 215.0, 222.0, 260.0, 305.0, 228.0, 141.0, 260.0, 232.0, 652.0, 133.0, 363.0, ],
	];
	chord_diagram(data, "#Harmonic_chord_diagram", pallete, intervals, "Beethoven");