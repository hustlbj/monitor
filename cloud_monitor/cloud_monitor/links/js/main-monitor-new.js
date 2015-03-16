var cluster = '';
var host = '';
var metric = '选择metric';
var group = '';
var step = '';
var lastClickRow1 = null;
var clickRow = null;

var tableInitParams = { 
    "sScrollX" : "100%",
    "sScrollXInner" : "100%",
    "bScrollCollapse" : true,
    "bJQueryUI" : true,
    "sPaginationType" : "full_numbers",
    "bDestroy": true,
    "bRetrieve": true,
    "oLanguage" : { 
        "sLengthMenu" : "  每页显示 _MENU_ ",
        "sZeroRecords" : "没有记录",
        "sInfo" : "显示 _START_ 到 _END_ 项记录，总共 _TOTAL_  项",
        "sInfoEmpty" : "没有记录",
        "sInfoFiltered" : "(从总共 _MAX_ 项记录中查找)"
    },  
    "sDom" : '<"H"Tfr>t<"F"ip>',
    "iDisplayLength" : 5,
    "oTableTools" : { 
        "sRowSelect" : "single",
        "aButtons" : []
    }   
};
//post to res_hostlist
function post_res_hostlist(){
	$.ajax({
		type: "POST",
		data: "host_type="+$("#adminSystemStatusNodeType").val(),
		url: "/res_hostlist/",
		dataType: "json",
		cache: false,
		success: function(data) {
			drawHostsInfo(data);
		},
		error: function(msg) {
			alert(msg);
		}
	});
}


function rowClick(){
	if(clickRow != null) {
		if(lastClickRow1 != null) {
			lastClickRow1.removeClass("highlighted");
		}
		lastClickRow1 = clickRow;
		var content = clickRow.children("td:eq(0)").text();
		if (content != '' && content != 'Host Name')
		{
			host = content;
			clickRow.addClass("highlighted");
			$.ajax({
				type: "POST",
				data: "host="+host,
				url: "/res_hostmetadata/",
				dataType: "json",
				cache: false,
				success: function(data) {
					drawHostDetail(data);	
				},
				error: function(error) {
				}
			});
		}
	}
}
//fill the hostinfo_table
function drawHostsInfo(data) {
	$("#hostinfo_table").dataTable().fnClearTable();
	//$("#hostinfo_table").dataTable().fnDestroy();
	if(data != null)
	{
		var time = Date.parse(new Date()) / 1000;
		for(var i = 0; i < data.length; i ++)
		{
			var newRow = [];
			var nets;
			var stat = 'off';
			//var minus = Math.abs(time - data[i]['time']);
			if(data[i]['stat'] == 'on')
				stat = '<font color="green">on</font>';
			else if(data[i]['stat'] == 'lost')
				stat = '<font color="yellow">lost</font>';
			else
				stat = '<font color="red">off</font>';
		
			newRow.push(data[i]['name'], 
				    data[i]['cpu_num'] + " * " + (data[i]['cpu_MHz']*0.001).toFixed(1),
				    //(data[i]['cpu_MHz']*0.001).toFixed(1),
				    (data[i]['mem_total']/1024/1024).toFixed(1),
				    //data[i]['disk_num'],
				    (data[i]['disk_size']/1024/1024).toFixed(1),
				    //data[i]['net_interfaces'],
				    stat);
			$("#hostinfo_table").dataTable().fnAddData(newRow);
		}
		
	}
	else
	{
		alert("no data!");
	}
	$("#hostinfo_table").dataTable(tableInitParams);
	$("hostinfo_table").show();
}

function drawHostDetail(data) {
	var os = data["os"];
	if(os)
		$("#host-os-info").html(os.replace(/\n/g, "<br/>"));
	else
		$("#host-os-info").html("issue:<br/>Unknown<br/><br/>version:<br/>Unknown");

	var cpu = data["cpu"];
	var system_info = '<div id="cpus">Nums: ' + cpu['cpu_num'] +
						'<br>Vendor ID: ' + cpu['vendor_id'] +
				        '<br>Width: ' + cpu['width'] +
						'<br>Model Name: ' + cpu['model_name'] +
						'</div>';
	$("#host-system-info").html(system_info);	
	var networks = data["network_interfaces"];
	var network_info = '<div id="networks">';
	for (var net in networks) {
	    network_info += 'Interface[' + net + ']' + ': ';
			for (var key in networks[net]) {
				network_info += '<br>&nbsp;&nbsp;&nbsp;&nbsp;' +
					key + ': ' + networks[net][key];
			}
		network_info += "<br>";
	}
	network_info += '</div>';
	$("#host-network-info").html(network_info);

	var disks = data["disks"];
	var disk_info = '<div id="disks"> Disks: ';
	for (var disk in disks) {
		disk_info += '<br>' + '&nbsp;&nbsp;Disk[' + disk + ']' + ' size: '
					+ (disks[disk]['size']*0.000001).toFixed(1) + 'GB';
		var used = 0.0
		for (var partition in disks[disk]['partitions']) {
			if (disks[disk]['partitions'][partition]['used'] != null)
				used += disks[disk]['partitions'][partition]['used'];
		}
		disk_info += ' used: ' + (used*0.000001).toFixed(1) + 'GB';
	}
	disk_info += "</div>";

	$("#host-disk-info").html(disk_info);
}

function drawHostMetric(data) {
	if (data.length > 0) {
		var x_description = new Array(data[0]['data'].length);
		
		for (var i=0; i<data[0]['data'].length; i ++) {
			x_description[i] = i+1;
			//x_description[i] = new Date(parseInt(data[0]['time'][i]) * 1000).toLocaleString().replace(/年|月/g, "-").replace(/日/g, " ");
		}
	
	//var optgroup = $("#"+metricname).parent();
	var optgroupID = document.getElementById(metric).parentNode.id;
	var unit = "";
	if (optgroupID == 'Mem') {
		if (metric != 'mem_usage') {
			unit = "KB";
		}
		else {
			unit = "%";
		}
	}
	else if (optgroupID == 'CPU') {
		unit = "%";
	}
	else if (optgroupID == 'Net') {
		if (metric == 'bytes_in' || metric == 'bytes_out') {
			unit = "B/s";
		}
		else {
			unit = "packages/s";
		}
	}
	else if (optgroupID == 'Disk') {
		if (metric != 'util') {
			unit = "";
		}
		else {
			unit = "%";
		}
	}
	else {
		unit = "";
	}
	
	$('#statusMonitorDetails').highcharts({
		title: {
			text: host + '监控数据统计',
			x: -20 //center
		},
		subtitle:{
			text: metric,
			x: -20 
		},
		xAxis: {
			categories: x_description
		},
		yAxis: {
			title: {
				text: metric + '(' + unit +')'
			},
			plotLines: [{
				value: 0,
				width: 1,
				color: '#808080'
			}]
		},
		tooltip: {
			valueSuffix: unit
		},
		legend: {
			layout: 'vertical',
			align: 'right',
			verticalAlign: 'middle',
			borderWidth: 0
		},
		series: /*[{
			name: "name1",
			data: data
		}, 
		{
			name: "name2",
			data: data
		}]*/data
	
	});
	}
	$("#statusMonitorDetails").show()
}

function refreshMetric() {
	if (host != '' && metric != '选择metric')
	{
		$.ajax({
		    type: "POST",
			data: {"host": host, "metric": metric, "step": step, "group": group},
		    url: "/res_hostmetric/",
			dataType: "json",
			cache: false,
		    success: function (data) {
			drawHostMetric(data);
			},
		    error: function (msg) {
		        alert(msg);
		    }
		});
	}
}

$(document).ready(function() {

post_res_hostlist();

$("#resourceRefresh").live("click", function() {
	post_res_hostlist();	
	rowClick();
	refreshMetric();	
});

$("#hostinfo_table").dataTable(tableInitParams);
$("#hostinfo_table tbody tr").live("click", function() {
	clickRow = $(this);
    	if(lastClickRow1 != clickRow) {
		rowClick();
		refreshMetric();
	}
});

$("#metricSelect").change(function() {
	metric = $("#metricSelect").val();
	step = $("#timeSelect").val();
	group = document.getElementById(metric).parentNode.id;
	if (host != '' && metric != '选择metric')
	{
		$.ajax({
		    type: "POST",
			data: {"host": host, "metric": metric, "step": step, "group": group},
		    url: "/res_hostmetric/",
			dataType: "json",
			cache: false,
		    success: function (data) {
			drawHostMetric(data);
			},
		    error: function (msg) {
		        alert(msg);
		    }
		});
	}
	else
	{
	}
});

$("#timeSelect").change(function() {
	metric = $("#metricSelect").val();
	step = $("#timeSelect").val();
	group = document.getElementById(metric).parentNode.id;
	if (host != '' && metric != '选择metric')
	{
		$.ajax({
		    type: "POST",
			data: {"host": host, "metric": metric, "step": step, "group": group},
		    url: "/res_hostmetric/",
			dataType: "json",
			cache: false,
		    success: function (data) {
			drawHostMetric(data);
			},
		    error: function (msg) {
		        alert(msg);
		    }
		});

	}
	else
	{
	}
});

//default active panel
$("#hostsDetails").addClass("activearea");

//Host info tabList
$("#systemHostInfo").accordion({
	fillSpace: true,
});

//openresourcepanel click
$("#openresourcepanel").click(function() {
	$(".activearea").hide();
	$(".activearea").removeClass("activearea");
	$("#hostsDetails").addClass("activearea");
	$(".activearea").show();
	post_res_hostlist();
});


});
