/*var systems = {
		"Web": {"time": "2014-05-03 00:00:00", "sysMan": "10.0.0.1", "comps": ["10.0.0.1", ["mysql", "httpd"], "10.0.0.2", ["mysql", "httpd", "heartbeat"]], "nums": 5, "value": 31, "detail": [
			"2014-05-01 00:10:30", ["10.0.0.1", ["mysql", "httpd"], "10.0.0.2", ["mysql", "httpd"]], 4, 15,
			"2014-05-02 20:00:00", ["10.0.0.1", ["mysql", "httpd"], "10.0.0.2", ["mysql", "httpd"]], 4, 7,
			"2014-05-03 00:00:00", ["10.0.0.1", ["mysql", "httpd"], "10.0.0.2", ["mysql", "httpd", "heartbeat"]], 5, 31]} ,

		"Hadoop": {"time": "2014-05-03 00:00:00", "sysMan": "10.0.0.3", "comps": ["10.0.0.3", ["NameNode", "TaskTracker", "SecondaryNameNode", "DataNode", "JobTracker"], "10.0.0.4", ["DataNode", "TaskTracker"], "10.0.0.5", ["DataNode", "TaskTracker"]], "nums": 9, "value": 499, "detail": [
			"2014-05-08 22:00:30", ["10.0.0.3", ["NameNode", "TaskTracker", "SecondaryNameNode", "DataNode", "JobTracker"], "10.0.0.4", ["DataNode", "TaskTracker"], "10.0.0.5", ["DataNode", "TaskTracker"]], 9, 511,
			"2014-05-11 13:00:00", ["10.0.0.3", ["NameNode", "TaskTracker", "SecondaryNameNode", "DataNode", "JobTracker"], "10.0.0.4", ["DataNode", "TaskTracker"], "10.0.0.5", ["DataNode", "TaskTracker"]], 9, 508,
			"2014-05-20 22:00:00", ["10.0.0.3", ["NameNode", "TaskTracker", "SecondaryNameNode", "DataNode", "JobTracker"], "10.0.0.4", ["DataNode", "TaskTracker"], "10.0.0.5", ["DataNode", "TaskTracker"]], 9, 499,]} ,

};
*/
var default_set_ = {
	anchors: ["RightMiddle", "LeftMiddle"],
	connector: "Straight",
	dragOptions: {},
	dropOptions: {},
	endpoint: "Dot",
	endpointStyle: {
		strokeStyle:"#7AB02C",
		fillStyle:"transparent",
		radius:5,
		lineWidth:2 
	},
	paintStyle: {
		lineWidth:4,
		strokeStyle:"#61B7CF",
		joinstyle:"round",
		outlineColor:"white",
		outlineWidth:2,
		cssClass: "aLine"
	},
};

var title_left_base = 30;
var title_top_base = 80;
//var title_height = 30;
//var title_width = 700;
var toggle_left = 300;
var flow_left_base = 40;
var flow_top_base = 60;
//var flow_width = 600;
//var flow_height = 60;

var window_base_left = 10;
var window_base_top = -5;
var window_width = 60;
var window_height = 60;
var left_inc = 240;
var top_inc = 200;
var sub_offset = 20;

var title_name_base = "title_";
var toggle_name_base = "toggle_";
var flow_name_base = "state_flow_";
var state_name_base = "state_";
var detail_name_base = "detail_";
var label_name_base = "label_";

function draw_fsm(seq, detail_fsm)
{
	var father_div = document.getElementById("state_flow_" + seq);
	for (var i = 0; i < detail_fsm.length / 4; i++) {
		//["10.0.0.100", ["comp1", "comp2"], "10.0.0.200", ["comp3", "comp4"]]
		var one_state_detail = detail_fsm[i * 4 + 1];
		//total state value = 15 = 2^4 - 1
		var value = detail_fsm[i * 4 + 3];
		//components' num = 4
		var num = detail_fsm[i * 4 + 2];
		var newDiv = document.createElement("div");
		newDiv.setAttribute("id", state_name_base + seq + "_" + i);
		//the last state
		if (i == detail_fsm.length / 4 - 1)
		{
			//all components are running, color is set to be green
			if (((1 << num) - 1) == value)
					newDiv.setAttribute("class", "component window normal_msg active big_font");
			//some components are not running, color is set to be red
			else
				newDiv.setAttribute("class", "component window wrong_msg active big_font");
		}
		//history states
		else
			newDiv.setAttribute("class", "component window normal_msg history big_font");
		newDiv.setAttribute("name", "window");
		newDiv.style.left = window_base_left + i * left_inc + "px";
		newDiv.style.top = window_base_top + "px";
		newDiv.style.width = window_width + "px";
		newDiv.style.height = window_height + "px";
		newDiv.innerHTML = value + "/" + ((1 << num) - 1);
		father_div.appendChild(newDiv);

		var newSubDiv = document.createElement("div");
		newSubDiv.setAttribute("id", detail_name_base + seq + "_" + i);
		newSubDiv.setAttribute("class", "div_overlay small_font ");
		newSubDiv.style.left =  window_width + sub_offset + "px";
		newSubDiv.style.top = "-5px";	

		for (var j = 0; j < one_state_detail.length / 2; j ++)
		{
			newSubDiv.innerHTML += "<span class='history'>" + one_state_detail[j * 2] + ":</span><br/>";

			var one_host = one_state_detail[j * 2 + 1];
			for (var k = 0; k < one_host.length; k ++)
			{
				//check this bit is 1 or 0, if 1, font color = green
				if ((1 << (num - 1)) & value)
					newSubDiv.innerHTML += "--<span class='normal_msg'>" + one_host[k] + "</span><br/>";
				//if 0, font color = red
				else
					newSubDiv.innerHTML += "--<span class='wrong_msg'>" + one_host[k] + "</span><br/>";
				num --;
			}	
		}
		newSubDiv.style.display = "none";
		newDiv.appendChild(newSubDiv);
	
	}
}
	
//hover function for a state window
function set_hover(div_name) 
{
	$("div[name='" + div_name + "']").each(function() {
		$(this).hover(
			function() {
				$(this).find(">div:first-child").show();
			},
			function() {
				$(this).find(">div:first-child").hide();	
			}
		);
	});
}

//draw title and state-flow one by one
function draw_titles(title_jsons) 
{
	if (title_jsons)
	{
		var i = 0;
		var father_div = document.getElementById("monitor");
		for (var key in title_jsons) 
		{
			//title div of every sub-system
			var newDiv = document.createElement("div");
			newDiv.setAttribute("id", title_name_base + i);
			newDiv.setAttribute("class", "div_title");
			newDiv.style.top = title_top_base + "px";
			newDiv.style.left = title_left_base + "px";
			if ((1 << title_jsons[key]["nums"]) - 1 == title_jsons[key]["value"])
			{
				newDiv.style.backgroundColor = "#d8dfee";
				newDiv.style.border = "#d8d3ee";
				newDiv.style.color = "black";
			}
			else
			{
				newDiv.style.backgroundColor = "#d8dfee";
				newDiv.style.border = "#d8d3ee";
				newDiv.style.color = "red";
			}
			newDiv.innerHTML = "<span style='position: absolute; width:500px; display: block; '>" + key + "&nbsp;&nbsp;" + title_jsons[key]["time"] + "</span>";
			father_div.appendChild(newDiv);

			var newSubA = document.createElement("a");
			newSubA.setAttribute("id", toggle_name_base + i);
			newSubA.setAttribute("name", "toggle");
			newSubA.setAttribute("href", "javascript:;");
			newSubA.setAttribute("target", "_self");
			//newSubA.style.position = "relative";
			//newSubA.style.left = toggle_left + "px";
			newSubA.style.float = "right";
			//newSubA.style.color = "white";
			newSubA.innerHTML = "展开";
			newDiv.appendChild(newSubA);

			//state flow div
			var newDiv1 = document.createElement("div");
			newDiv1.setAttribute("id", flow_name_base + i);
			newDiv1.setAttribute("class", "div_state_flow");
			//newDiv1.style.left = flow_left_base + "px";
			//newDiv1.style.top = flow_top_base + "px";
			father_div.appendChild(newDiv1);

			//draw states of one state-flow
			draw_fsm(i, title_jsons[key]["detail"]);

			i ++;
		}
		//add the hover function to each state window
		set_hover("window");
	}
}

function draw_connection(title_jsons) 
{
	if (title_jsons)
	{
		var seq = 0;
		for (var key in title_jsons)
		{
			for (var i = 0; i < title_jsons[key]["detail"].length / 4 - 1; i ++)
			{
				var conn = jsPlumb.connect(
				{
  					source: state_name_base + seq + "_" + i,
  					target: state_name_base + seq + "_" + (i + 1),	
  					overlays: [
  						["Arrow", {location: -1}],
						["Label", {location: 0.5, id: label_name_base + seq + "_" + i, cssClass: "aLabel"}]
					],
				}, default_set_
				);
				conn.getOverlay(label_name_base + seq + "_" + i).setLabel(title_jsons[key]["detail"][i * 4]);
			}
			seq ++;
		}
	}
}

function add_toggle(button_name)
{
	$("a[name='" + button_name + "']").each(function() {
		$(this).parent().next().hide();
		$(this).click(function () {
			$(this).text($(this).parent().next().is(":hidden")?"收起":"展开");
			$(this).parent().next().slideToggle();
		});
	});		
}


function draw_fsms(data) {
	/*if data is an array*/
	var items_page = new Array(data.length / 2);
	for(var i = 0; i < data.length / 2; i ++) {
		items_page[data[i*2]] = data[i*2+1];
	}	
	document.getElementById("monitor").innerHTML = "";
	//draw_titles(data);
	draw_titles(items_page);
	jsPlumb.ready(function () {
		draw_connection(items_page);
	});
	add_toggle("toggle");
}

function request_fsms() {
	$.ajax({
		type: "POST",
		data: {},
		url: "/comp_getfsms/",
		dataType: "json",
		cache: false,
		success: function(data) {
			draw_fsms(data);
		},
		error: function(msg) {
		}
	});
}
/*
$(document).ready(function (){
	request_fsms();
	$("#componentsRefresh").click(function(){
		request_fsms();
	});
});
*/
		/*
		draw_fsm(0, detail1, 3);
		
		set_hover("window");
		jsPlumb.ready(function () {
			for (var i = 0; i < detail1.length / 4 - 1; i ++)
			{
				var conn = jsPlumb.connect(
				{
  					source: "state_0_" + i,
  					target: "state_0_" + (i + 1),	
  					overlays: [
  						["Arrow", {location: -1}],
						["Label", {location: 0.5, id: "label_0_" + i, cssClass: "aLabel"}]
					],
				}, default_set_
				);
				conn.getOverlay("label_0_" + i).setLabel(detail1[i * 4]);

			}
		
		});

		$("#state_flow_0").hide();
		$("#toggle_0").click(function () {
			$(this).text($("#state_flow_0").is(":hidden")?"收起":"展开");
			$("#state_flow_0").slideToggle();
		});*/
/*
	draw_titles(systems);
	jsPlumb.ready(function () {
		draw_connection(systems);
	});
	add_toggle("toggle");*/

