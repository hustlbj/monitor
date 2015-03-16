$(document).ready(function(){
	var dataTable_cluster;
	var service_clusterUrl="/ClusterServiceMonitor/getServiceStatus";
        var service_logUrl="/ClusterServiceMonitor/serviceLogToHtml?sitename=test";
	var cluster_state_message;
	var cluster_service_error_list = [];

	var clusterservice_tab_content=
		'<div style="font-size:80%; padding-top:10px;"> \
	   		<div id="service_monitor_tab"> \
 			<div class="subtable-title" id="service_monitor_error_head">错误信息</div> \
				<div id="service_monitor_error_div" style="min-height:50px">\
				</div>\
 			<div class="subtable-title" ><span>服务监控</span>&nbsp;&nbsp;&nbsp;&nbsp;<span id="serviceUpdate" style="color:green;font-size:12px"></span></div> \
				<div id="service_monitor_div" style="min-height:150px">\
				<table id="service_monitor" class="subtable"  >\
				</table>\
				</div>\
		</div>   \
	</div>';

	function openServicePanel(){
		$(".activearea").hide();
		$(".activearea").removeClass();
		$("#clusterService").addClass("activearea");
		getClusterInfo();
		$(".activearea").show();
	}
	$('#openservicepanel').click(openServicePanel);
	$("#clusterService").hide();
	
	function get_pb(util){
		var ret =
		  	'<div style="height:10px" class="ratiobar ui-progressbar ui-widget ui-widget-content ui-corner-all" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="'+util+'">\
		   	<div class="ui-progressbar-value ui-widget-header ui-corner-left ui-corner-right" style="width: '+util+'%;"/>\
		  	<span style="position:relative;left:90px;top:-4px;font-size:0.6em">'+util+'%</span>\
		   	</div>\
		   	</div>';
		return ret;
	}
	
	function get_span(span){
		if(span =="ON"){
			return '<span style="color:green">ON</span>';
		}
		else if( span =="OFF"){
			return '<span style="color:red">OFF</span>';
		}
		else{
			return '<span>Unknow</span>';
		}
	}
	
	function listToTable(service_list ){
		var length=service_list.length;
		var td_head='<td class="head">';
		var td_info='<td style="letter-spacing: 0.1mm ">';
		var ret="";
		cluster_service_error_list = [];
		for (var i=0;i<length;i++){
                        temp = service_list[i];
                        ret = ret+'<tr>'+td_head+temp["service"]+':</td>'+td_info+get_span(temp["status"])+'</td>'+td_info+temp["script"]+'</td>';
                        var color = "green";
                        if(temp["status"] == "OFF"){
                                color = "red";
				cluster_service_error_list.push(temp["service"]);
                        }
                        ret = ret+'<td style="letter-spacing: 0.1mm ;min-width: 110px;">'+'进程pid:'+'<span style="color:'+color+'">'+temp["pid"]+'</span></td></tr>';
                }
		return ret;
	}

	function timeFormat(time){
		var year=time.getFullYear();
		var month = time.getMonth()+ 1;
		if (month<10)
			month='0'+month;
		var day = time.getDate();
		if (day<10)
			day = '0'+day;
		var hour=time.getHours();
		if (hour<10)
			hour='0'+hour;
		var min=time.getMinutes();
		if (min<10)
			min='0'+min;
		var sec = time.getSeconds();
		if (sec < 10)
			sec='0'+sec;
			
		var clock = year+"/"+month+"/"+day+" "+hour+":"+min+":"+sec;
		
		return clock;
	}
	
	function warningdictToTable(warning_dict){
		var td_head='<td style="font-weight: bold;etter-spacing: 0.9px;width: 20%;">';
		var td_info='<td style="letter-spacing: 0.1mm ">';
		var ret = "";
		var time = new Date();
		var clock = timeFormat(time);
		for (var key in warning_dict){
        		var d = warning_dict[key];
			ret=ret+'<tr>'+td_head+"节点:"+key+'</td>'+td_info+'预警:'+d['Type']+'</td>'+td_info+'利用率:'+d['Value']+'%</td>'+td_info+'阈值:'+d['Thre']+'%</td>'+td_info+'时间:'+clock+'</td>';
		}
		return ret;
	}	

	function clusterElementArray(cluster_key,clusterinfo){
		var name = cluster_key;
		var cpu_util,mem_util,disk,show_status,usernumber,jobsrunning;
		var cluster=clusterinfo;
		
		if (cluster.Status == "ON"){
			cpu_util = Math.round(parseInt(cluster.CPUUsed)/parseInt(cluster.CPUTotal)*100);
			mem_util = Math.round(parseInt(cluster.MemUsed)/parseInt(cluster.MemTotal)*100);
			disk = parseInt(cluster.DiskTotal)/1024/1024;
			disk = disk.toFixed(2) + " GB";
			usernumber=cluster.UsersTotal;
			jobsrunning=cluster.JobsRunning;
			show_status="<span style='color:green'>ON</span>";
		}
		else{
			cpu_util=0;
			mem_util=0;
			disk="";
			usernumber=0;
			jobsrunning=0;
			show_status="<span style='color:red'>"+cluster.Status+"</span>";
		}	
		var pb_mem = get_pb(mem_util);
		var pb_cpu = get_pb(cpu_util);
		return [name,pb_cpu,pb_mem,disk,usernumber,jobsrunning,show_status ];
	}

	function setTableSelection(table) {
		$("#tbodycluster tr",table).live("click" ,function(){
			var tab = $(table).dataTable();
			$(tab.fnSettings().aoData).each(function() {
				$(this.nTr).removeClass('row_selected');
			});
			$(this).addClass('row_selected');
			tableClusterClicked(table);
		});
	}
	
	function tableClusterClicked(table) {
		var selectTable =table.dataTable();
		var trSelected = fnGetSelected(selectTable);
		var a = $('td',trSelected);
		if (a.length == 0) {
			alert("请选择一台主机");
			return;
		}
		sitename = $(a[0]).text();
		state = $(a[6]).text();
		loadClusterHostStatus(sitename,state);
	}
	function loadClusterHostStatus(sitename,state){
		$("#monitorconsole_tab").addClass("activearea");
		$(".activearea").show();
		$("#service_monitor").empty();
		cluster_state_message = "";
		//if ( state == "OFF"){
		//	cluster_state_message = "站点失效:";
		//}
		//else{
		//	cluster_state_message = "";
		//}
		//$("#service_monitor_alert").empty();
		$.get(service_clusterUrl,
			{cluster:sitename},
			loadAllServiceTable,
			'json'
		);
	}

	function loadAllServiceTable(data){
		var service_data = data["service"];
		var timestamp = parseInt(data["timestamp"]);
		var localTime = new Date(timestamp*1000);
		var stringTime = timeFormat(localTime)+"更新";
		var now = new Date().getTime()/1000;
		var message = "";
		$("#service_monitor_error_head").hide();
		$("#service_monitor_error_div").hide();
		$("#serviceUpdate").html("");
		$("#service_monitor").html(listToTable(service_data ));	
		$("#serviceUpdate").html(stringTime);
		if ( now - localTime > 60 ){
			cluster_state_message = "站点失效：请检查站点网络连接";
		}
		else{
			cluster_state_message = "";
		}
		if ( cluster_state_message !=""){
			message = "";
			message = "<font style='color:red;font-size:14px;padding:7px 15px'>"+cluster_state_message+"</font><br />";
		}
		if ( cluster_service_error_list.length != 0){
			message += "<font style='color:red;font-size:14px;padding:7px 15px'>请检查以下服务:"+cluster_service_error_list.toString()+"</font><br />";
		}
		if ( message != ""){
			$("#service_monitor_error_div").empty();
			$("#service_monitor_error_div").html(message);
			$("#service_monitor_error_head").show();
			$("#service_monitor_error_div").show();
		}
	}
	
	function fnGetSelected(oTableLocal) {	   
		var aReturn = new Array();
		var aTrs = oTableLocal.fnGetNodes();
		for (var i = 0; i < aTrs.length; i++) {
			if ($(aTrs[i]).hasClass('row_selected')) {
			aReturn.push(aTrs[i]);
			}
		}
		return aReturn;
	}
	
	function updateClusterView(item_dict,dataTable){
		var cluster_list_array=[];
		items = eval('('+item_dict+')');
		if (allsites.length==1){
		    cluster_list_array.push(clusterElementArray( allsites[0], items[allsites[0]]));
		}
		else{
		    for( var key in items){
			    cluster_list_array.push(clusterElementArray( key, items[key]));
		    }
		}
		if(dataTable){
			dataTable.fnClearTable();
			dataTable.fnAddData(cluster_list_array);
			dataTable.fnDraw(true);
		};
	}
	
	
	function getClusterInfo() {
		var cluster_data = $("#clusterService").data("info");
		if ( cluster_data ){
			loadClusterTable(cluster_data);
			return;
		}	
		$.ajax({
			url:"/ClusterNodes/getClusterNodesinfoCache",
			type:"GET",
			data:{},
			dataType:"json",
			timeout:80000,
			success:function(data){
				$("#clusterService").data("info",data);
				loadClusterTable(data);
			}		 
		});
	}

	$("#monitorconsole_tab").html(clusterservice_tab_content);
	$("service_monitor_tab").hide();		
	dataTable_cluster=$("#adminClusterServiceMonitorTable").dataTable({
		"bJQueryUI": true,
		"bSortClasses": false,
		"bAutoWidth":false,
		"sPaginationType": "full_numbers",
		"aoColumnDefs": [
			{ "sWidth": "60px", "aTargets": [0] },
			{ "sWidth": "100px", "aTargets": [3,4] },
			{ "sWidth": "120px", "aTargets": [5] },
			{ "sWidth": "220px", "aTargets": [1,2] }
			]
	});

	function loadClusterTable(clusterinfo) {
		updateClusterView(clusterinfo, dataTable_cluster);
		setTableSelection($("#adminClusterServiceMonitorTable"));
	}
   
	//DELAY FUNCTIONS: RUN AFTER GLOBALVAR.JS

	$("#adminSystemServiceRefreshTableButton").click(function(){
		$("#clusterService").data("info",null);
		openServicePanel();
	});
	
/////Add Dialog////
        $("#adminServiceLogDialog").dialog({
                width: 700,
                height: 500,
                autoOpen: false,
                modal: true,
                title: 'Service Monitor Log',
                buttons:{
                        Close: function(){
                                $(this).dialog("close");
                        },
                        Refresh: function(){
                                $("#adminServiceLogTextArea").attr("src","#");
                                $("#adminServiceLogTextArea").attr("src",service_logUrl);
                        }
                }
        });
        $("#adminServiceLogButton").click(function(event){
                $("#adminServiceLogTextArea").attr("src",service_logUrl);
                $("#adminServiceLogDialog").dialog("open");
        });
		

		
});
