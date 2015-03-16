$(document).ready(function(){
	var isHost = false;
	var sitename = '';
	var selectedId = '';
	var chart = null;
	var metricDesc = null;
	var urlTemplate_ori = "/SystemStatus/getStats?sitename={sitename}&host_id={host}&metric_name={metric}";	
	var allVmpoolUrl = '/IaaS/getVmsInfo',
		allHostpoolUrl = '/IaaS/getHostpoolInfo',
		hostInfoUrl = '/SystemStatus/getHostInfo',
		machinesetUrl ='/SystemStatus/MachineSet',
		machineinstallUrl ='/SystemStatus/MachineInstall',
		deletemachineUrl ='/SystemStatus/DeleteMachine',
		addmachineUrl='/SystemStatus/AddMachine',
		machinetableUrl ='/SystemStatus/MachineTable',
		metricListUrl = '/SystemStatus/getMetricList';
		AddClusterNode='/ClusterNodes/addClusterNode'

	// Variable for LOG VIEW
	var plotList = {action: null,
			site: null};
	var query_log_num = 50;

	function bindEvents() {
		$('#statusMonitorSetting select').change(function (e) {
			$("#metricDescription").text( metricDesc[$("#metricSelect").val()] );
			var metricName = $('#metricSelect').val();
			if (!metricName.length)
				return;
			var metricGrp = $('#metricSelect').find('option:selected').parent().attr('label');

			var metric = $('#adminSystemStatusGraphContainer').data(selectedId+'_metricGroups')[metricGrp][metricName];
			metric.metric = metricName;
			metric.host = selectedId;
			var timeRange = parseInt($('#timeSelect').val());
			var step = 15;
			if (timeRange >= 1*3600*24)
				step = 3600;	
			else if (timeRange > 3600)
				step = 60;
			else
				step = 15;
			urlTemplate = urlTemplate_ori.replace("{sitename}", sitename);
			drawPerfChart(selectedId, metric, step, timeRange);
		});
	}

	function reDrawTables(){
		$('#adminComputingResourceTable').dataTable().fnDraw();
		$('#adminSystemStatusClusterTable').dataTable().fnDraw();
		$('#adminSystemStatusHostTable').dataTable().fnDraw();
		$('#adminSystemStatusVMTable').dataTable().fnDraw();
		$('#adminGeneralTracesTable').dataTable().fnDraw();
		$('#adminDetailsTracesTable').dataTable().fnDraw();
                $('#virtualmachine').dataTable().fnDraw();
	}
	
	function drawPerfChart(host, metric, step, timeRange) {
		if (chart instanceof PerfChart) {
			chart.unsetRealTime();
		}
		chart = new PerfChart({
			placeholder: '#statusMonitorDetails',
			step: step,
			maxRange: (timeRange > 0) ? timeRange : 3600,
			metrics: [metric],
			urlTemplate: urlTemplate,    
			options: {        
				legend : {
				position: 'nw',
				backgroundOpacity: 0.1
				},
				xaxis: {
				//tickLength: 0
				},
				series: {
					shadowSize: 0,
					lines: {
						lineWidth: 2,
						fill: true
					}
				},
				//colors: ['ironblue']
			}
		});
		
		if (timeRange > 0) {
			chart.plotOnce();
		} else {
			chart.setRealTime(15000);
		}
	}

	function getVmsPoolInfo() {
		$.get(allVmpoolUrl,
			{
			   sitename: sitename,
			},
			function (data){
				if (data[0])
					loadVMsTable(data[1]);
			},
			'json');
			
	}

	function loadVMsTable(vmsInfo) {

	/*	for (var k = $('#adminSystemStatusVMTable').dataTable().fnSettings().aoData.length - 1; k >= 0; k--) {
			var name = $('#adminSystemStatusVMTable').dataTable().fnSettings().aoData[k]._aData[1];
			if (name == sitename) {
				var node = $('#adminSystemStatusVMTable').dataTable().fnGetNodes(k);
				$('#adminSystemStatusVMTable').dataTable().fnDeleteRow(node);
			}
		}*/
		$('#adminSystemStatusVMTable').dataTable().fnClearTable();
		for (var i = 0; i < vmsInfo.length; i++) {
			var d = vmsInfo[i];
			var vmid = d.guid;
			var owner = d.owner;
			var vcpu = d.vcpu;
			var mem = d.memory;
			var stat = d.stat;
			var row = [vmid, sitename, owner, vcpu, mem, stat];
				
			$('#adminSystemStatusVMTable').dataTable().fnAddData(row);
				
		}
		setTableSelection($('#adminSystemStatusVMTable'));
	
		$('#adminSystemStatusVMTable').dataTable().fnDraw();
	}

	function getHostsPoolInfo() {
		$.get(allHostpoolUrl,
		{
			sitename: sitename,
		},
		function (data){
			if (data[0])
				loadHostsTable(data[1]);
		},
		'json');
	}

	function loadHostsTable(hostsInfo) {

		/*for (var k = $('#adminSystemStatusHostTable').dataTable().fnSettings().aoData.length - 1; k >= 0; k--) {
			var name = $('#adminSystemStatusHostTable').dataTable().fnSettings().aoData[k]._aData[1];
			if (name == sitename) {
				var node = $('#adminSystemStatusHostTable').dataTable().fnGetNodes(k);
				$('#adminSystemStatusHostTable').dataTable().fnDeleteRow(node);
			}
		}*/
		$('#adminSystemStatusHostTable').dataTable().fnClearTable();
		for (var i = 0; i < hostsInfo.length; i++) {
			var d = hostsInfo[i];
			var hostid = d.hostname;
			var totalcpu = d.totalCpu;
			var usedcpu = d.usedCpu;
			var totalmem = parseInt(d.totalMemory/1024);
			var freemem = parseInt(d.freeMemory/1024);
			var vms = d.virtualMachines;
			var row = [hostid, sitename, totalcpu, usedcpu, totalmem, freemem, vms];
				
			$('#adminSystemStatusHostTable').dataTable().fnAddData(row);
				
		}
		setTableSelection($('#adminSystemStatusHostTable'));
		$('#adminSystemStatusHostTable').dataTable().fnDraw();
	}

	function SetTableSelection(table) {
		$(table).children('tbody').click(function(evt) {
			var tab = $(table).dataTable();
			$(tab.fnSettings().aoData).each(function() {
				$(this.nTr).removeClass('row_selected');
			});
			$(evt.target.parentNode).addClass('row_selected');

			TableTrClicked(table);
		});
	}
	function setTableSelection(table) {
		$(table).children('tbody').click(function(evt) {
			var tab = $(table).dataTable();
			$(tab.fnSettings().aoData).each(function() {
				$(this.nTr).removeClass('row_selected');
			});
			$(evt.target.parentNode).addClass('row_selected');

			tableTrClicked(table);
		});
	}

	function TableTrClicked(table) {
		var selectTable =table.dataTable();
		var trSelected = fnGetSelected(selectTable);
		var a = $('td',trSelected);
		//alert(a.length);
		selectedId = $(a[0]).text();
		sitename = $(a[1]).text();
		$.plot($("#statusMonitorDetails"), []);
		$("#metricDescription").empty();
		loadVmStatus(sitename, selectedId);
	}

	function tableTrClicked(table) {
		var selectTable =table.dataTable();
		var trSelected = fnGetSelected(selectTable);
		var a = $('td',trSelected);
		if (a.length == 0) {				
			alert("请选择一台主机");
			return;
		}
		selectedId = $(a[0]).text();
		sitename = $(a[1]).text();
		$.plot($("#statusMonitorDetails"), []);
		resetVmStatusContainer();
		$("#metricDescription").empty();
		loadVmStatus(sitename, selectedId);
	}
	
	function getSystemHostInfo(sitename, vmid, callback){
		var hostInfo = $('#adminSystemStatusGraphContainer').data(selectedId+'_hostInfo');
		if (hostInfo) {
			renderHostInfo(hostInfo, callback);
		} else {

			$.get(hostInfoUrl,
				{
				sitename:   sitename,                
				vmid:       vmid
				},
				function(serverResponse) {
					if(serverResponse[0]==true){
					var hostInfo = serverResponse[1];
					$('#adminSystemStatusGraphContainer').data(selectedId+'_hostInfo', hostInfo);
					renderHostInfo(hostInfo, callback);
					}
					
				},
				'json');		
		}
	}

	function loadVmStatus(sitename, vmid) {
		getSystemHostInfo(sitename, vmid, systemHostInfoDivCreate);
		var metricGroups = $('#adminSystemStatusGraphContainer').data(selectedId+'_metricGroups');
		if (metricGroups) {
				$('#metricSelect').children('option:first-child').siblings().remove();
				loadMetrics( metricGroups, $('#metricSelect') );
				if (chart instanceof PerfChart)
					chart.unsetRealTime();
		} else {
				$.get(metricListUrl,
					{
						sitename:   sitename,
						vmid:       vmid
					},
					function (response) {
						if (response[0]) {
						$('#metricSelect').children('option:first-child').siblings().remove();
						var metricGroups = groupMetrics(response[1]);
						$('#adminSystemStatusGraphContainer').data(selectedId+'_metricGroups', metricGroups);
						loadMetrics( metricGroups, $('#metricSelect') );
						if (chart instanceof PerfChart)
							chart.unsetRealTime();
						}
					},
					'json'
				);
				
				$.ajax({
					url:"/SystemStatus/getMetricDescription?sitename="+sitename,
					type:"GET",
                			data:{},
					dataType:"json",
					timeout:3000,
					success:function(data){
						data = eval(data);
						metricDesc = data[1];
					}
        			});	
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

	function isArray(o){
			return Object.prototype.toString.call(o) == '[object Array]';
	}


	function systemHostInfoDivCreate(hostInfoDiv,titleInfo,detailInfo){
		var containerDiv = document.createElement("div");
		containerDiv.className = "accordingContentContainer";
		
		var clearDiv = document.createElement("div");
		clearDiv.className = "accordingEndClear";
		
		var titleDiv = document.createElement("div");
		titleDiv.className = "accordingContentTile";
		titleDiv.appendChild( document.createTextNode(titleInfo));

		var detailDiv = document.createElement("div");
		detailDiv.className = "accordingContentDetail";
		if(isArray(detailInfo)){		
			for(var i = 0;i< detailInfo.length;i++){
				detailDiv.appendChild(document.createTextNode(detailInfo[i]));
				if(i!=detailInfo.length-1){
					detailDiv.appendChild(document.createElement('br'));
				}
			}
				
		}else{
			detailDiv.appendChild(document.createTextNode(detailInfo));	
		}
		
		containerDiv.appendChild(titleDiv);
		containerDiv.appendChild(detailDiv);
		containerDiv.appendChild(clearDiv);
		
		hostInfoDiv.appendChild(containerDiv);
	}

	function resetVmStatusContainer() {
			$('#systemHostInfo').children('div').empty();
	}
	
	function renderHostInfo(hostInfo, callback) {
		resetVmStatusContainer();
		var hostsystemdiv = document.getElementById("host-system-info");
		var hostdiskdiv = document.getElementById("host-disk-info");	
		var hostnetworkdiv = document.getElementById("host-network-info");	

		// system info
		callback(hostsystemdiv,"ID",hostInfo.id);
		callback(hostsystemdiv,"处理器",hostInfo.cpu.model_name);
		callback(hostsystemdiv,"处理器数",hostInfo.cpu.cpu_num);
		callback(hostsystemdiv,"内存",hostInfo.mem_total+' KB');
		//net info
		for(var title in hostInfo.network_interfaces){
			var detailDict = new Array();
			var netDetailList = ['hwaddr','inet_addr','bcast','mask','mtu','scope'];						
			for(var i =0;i< netDetailList.length;i++){							
			if(typeof hostInfo.network_interfaces[title][netDetailList[i]] === 'undefined'){
				continue;
			}
				detailDict.push(netDetailList[i]+":"+hostInfo.network_interfaces[title][netDetailList[i]]);
			}						
			callback(hostnetworkdiv,title,detailDict);												
		}
		//disk info
		var diskDetailList = ['size','used','avail'];
		for(var dtitle in hostInfo.disks){						
			var theDisk = hostInfo.disks[dtitle];
			if (theDisk.partitions) {
			for (var pname in theDisk.partitions) {
				//ptitle = 'dev/' + pname;
				ptitle = pname;
				var pdetail = [];
				for (var j = 0; j < diskDetailList.length; j++) {
				var thePart = theDisk.partitions[pname];
				if (thePart[diskDetailList[j]] === undefined)
					continue;
				pdetail.push(diskDetailList[j] + ':' + parseInt(parseInt(thePart[diskDetailList[j]])/1024) + ' MB')
				}
				callback(hostdiskdiv, ptitle, pdetail);
			}
			}
		}
	}
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	

	function installGetinfo(){
		$('#adminComputingResourceTable').dataTable().fnDraw();
		$.get(machinetableUrl,{idx : ''},loadinstalltable,'json');
	}

	function loadinstalltable(insinfo){
		$('#adminComputingResourceTable').dataTable().fnClearTable();
		for(var i = 0;i < insinfo.length; i++){
			var d = insinfo[i];
			var idx =d.idx;
			var cluster =d.cluster;
			var host = d.host;
			var response = d.bmc;
			var power = d.power;
			var machinestatus = d.machinestatus;
			var selected = "<input type='checkbox' class='choose'   name='checkbox1' value="+host+"/>";
			var row = [idx,selected,cluster,host,response,power,machinestatus];
			$('#adminComputingResourceTable').dataTable().fnAddData(row);
		}
		SetTableSelection($('#adminComputingResourceTable'));
		 $("#adminComputingResourceTable tr").click(function(event){
                        var table =$("#adminComputingResourceTable").dataTable();
                        if ($(event.target.parentNode).hasClass('row_selected')) {
                   		 $(event.target.parentNode).removeClass('row_selected');
                	}
                	else {
                    		$(event.target.parentNode).addClass('row_selected');
                	}
                        var trSelected = fnGetSelected(table);
                        var a = $('td',trSelected);
                        if (a.length == 0) {
                                return 0;
                        }
                });
	
		$('#adminComputingResourceTable').dataTable().fnDraw();
	}
        $("#PowerOn").click(PowerOn);
        $("#PowerOff").click(PowerOff);
        $("#PowerReset").click(PowerReset);
        $("#Installnode").click(Install);
	$('#addhost').click(function() {
                $("#addhostfloat-back").css("width","740px");
                $("#addhostfloat-mainDiv").css("width","720px");
                $("#addhostfloat-mainDiv-top").css("width","720px");
		$(".float-div-back").show();
		$("#addhost-div").show();
	});

	$('#InstallLog').click(function()
	{
		data="<table class='subtable' ><tr><td class='info'>15:25:59  设置PXE启动  </td></tr><tr><td>15:25:59 重新启动</td></tr> <tr><td>15:26:19 从dhcp服务器获取ip</td></tr></td></tr><tr><td>15:26:20 获取安装配文件ks.cfs</td></tr></td></tr><tr><td>15:37:12 获取系统安装镜像</td></tr></td></tr><tr><td>15:53:18 安装系统及其相关软件</td></tr></td></tr><tr><td> 16:28:28 yum 的升级</td></tr></td></tr><tr><td>16:30:50 开始拷贝crane安装包</td></tr></td></tr><tr><td>16:31:46 安装crane的环境的相关软件及其配置环境</td></tr></td></tr><tr><td>16:36:18 安装成功，系统开始重启</td></tr></table>";	
		$("#MachineLog").html(data);
	});

        $('.dialog-bottom  a').click(function() {
                var thisvalue = $(this).attr("value");
                if(thisvalue=="next2"){
			if ($('#selectschool').val() == '' || $('#mbcip').val() == '' || $('#hostname').val() == ''|| $('#username').val() == ''|| $('#ip').val() == ''|| $('#password').val() == '') {
				alert("请填写完整信息!");
				return false;
			}	
			vselectschool = $('#selectschool').val();
			vmbcip = $('#mbcip').val();
			vhostname = $('#hostname').val();
			vusername = $('#username').val();
			vip = $('#ip').val();
			vpassword = $('#password').val();
			$('#showschool').val(vselectschool);
			$('#showhost').val(vhostname);
			$('#showip').val(vip);
			$('#showmbcip').val(vmbcip);
			$('#showuser').val(vusername);
			$('#showpassword').val(vpassword);	
			$("#hoststep2").css("display","block");
                        $("#hoststep1").toggle("slow");	
                }
                else if(thisvalue=="backtohoststep1"){
                         $("#hoststep2").css("display","none");
                         $("#hoststep1").toggle("slow");
                }
                else if(thisvalue=="nexttotwo"){
                        if ($('#selectschool1').val() == '' || $('#outernetip').val() == '' || $('#IaasDns').val() == ''|| $('#webpaasdns').val() == '') {
                                alert("请填写完整信息!");
                                return false;
                        }
                        vselectschool1 = $('#selectschool1').val();
                        vouternetip = $('#outernetip').val();
                        vIaasDns = $('#IaasDns').val();
                        vwebpaasdns = $('#webpaasdns').val();
                        $('#showschool1').val(vselectschool1);
                        $('#showouterip').val(vouternetip);
                        $('#showiaasdns').val(vIaasDns);
                        $('#showpaasdns').val(vwebpaasdns);
                        //$("#installnodestep2").css("display","block");
                        $("#installnodestep2").show();
                        $("#installnodestep1").toggle("slow");
			
			var rt=$.ajax({
				url:"/ClusterNodes/addClusterNode",
				type:"post",
        		        data: {   name:"tsu",
					 school:"清华大学",
					 location:"北京",
					 ip:"166.111.131.47",
					 information:"清华大学计算节点",
					 imgpath:"",
					 level:"1",
					computing:"1000",
					storage:"5T"},
                                        async:false,
				dataType:"json"
			}).responseText;
			
                }
                else if(thisvalue=="backtoinstallnodestep1"){
                         $("#installnodestep2").css("display","none");
                         $("#installnodestep1").toggle("slow");
                }
        });
	 $('#InstallNode').click(function() {
		$("#installnodefloat-back").css("width","740px");
		$("#installnodefloat-mainDiv").css("width","720px");
		$("#installnodefloat-mainDiv-top").css("width","720px");
                $(".float-div-back").show();
                $("#installnode-div").show();
                
        });
	$("#closeinstallnodepage").click(function(){
		$("#installnode-div").hide();
		$(".float-div-back").hide();
	});
       $("#installnodeconfirmbutton").click(function(){
                $("#installnode-div").hide();
                $(".float-div-back").hide();
        });
       $("#addhostconfirmbutton").click(function(){
                $("#addhost-div").hide();
                $(".float-div-back").hide();
        });
/*
	$('.dialog-bottom  a').click(function() {
                var thisvalue = $(this).attr("value");
		if(thisvalue=="next2"){
			$("#hoststep2").css("display","block");
			$("#hoststep1").toggle("slow");
		}systemHostInfo
		else if(thisvalue=="backtohoststep1"){
			 $("#hoststep2").css("display","none");
                         $("#hoststep1").toggle("slow");
		}
	});*/
	$('.closeFloat').click( function() {
		$("#addhost-div").hide();
					
		$(".float-div-back").hide();
	} );
	$("#delhost").click(delhost);
	
	function delhost(){
	 	var array =new Array();
               	var falg=0;
               	$(".choose").each(function () {
        	       	if ($(this).attr("checked")) { 
			var value=$(this).val();
			value=value.substring(0,value.length-1);
		 	array.push(value);
                	falg += 1; 
			}	
		});  
	for (i in array)
	{
		var array_text = JSON.stringify(array[i]);
		$.ajax({
			url:"/SystemStatus/DeleteMachine",
			type:"GET",
        	        data: {   sitename:"hust",
				  hostName: array_text},
			dataType:"json",
			});
	}
		alert("success");
	}
	function Install(){
	 	var array =new Array();
               	var falg=0;
               	$(".choose").each(function () {
        	       	if ($(this).attr("checked")) { 
			var value=$(this).val();
			value=value.substring(0,value.length-1);
		 	array.push(value);
                	falg += 1; 
			}	
		});  
	for (i in array)
	{
		var array_text = JSON.stringify(array[i]);
		$.ajax({
			url:"/SystemStatus/MachineInstall",
			type:"GET",
        	        data: {   sitename:"hust",
				  hostName: array_text},
			dataType:"json",
			});
		alert("success");
	}
/*	var array_text = JSON.stringify(array);
	alert(array_text);
	$.ajax({
		url:"/SystemStatus/MachineInstall",
		type:"GET",
                data: {   sitename:"hust",
			  hostName: array_text},
		dataType:"json",
		});*/
	}
	
	function PowerOff(){
	 	var array =new Array();
               	var falg=0;
               	$(".choose").each(function () {
        	       	if ($(this).attr("checked")) { 
			var value=$(this).val();
			value=value.substring(0,value.length-1);
		 	array.push(value);
                	falg += 1; 
			}	
		});  
	for (i in array)
	{
		var array_text = JSON.stringify(array[i]);
		$.ajax({
			url:"/SystemStatus/MachineSet",
			type:"GET",
        	        data: {   sitename:"hust",
				  hostName: array_text,
                          	  flag: "off" },
			dataType:"json",
			});
		alert("success");
	}
/*	var array_text = JSON.stringify(array);
	alert(array_text);
	$.ajax({
		url:"/SystemStatus/MachineSet",
		type:"GET",
                data: {   sitename:"hust",
			  hostName: array_text,
                          flag: "off" },
		dataType:"json",
		});*/
	}

	function PowerReset(){
	 	var array =new Array();
               	var falg=0;
               	$(".choose").each(function () {
        	       	if ($(this).attr("checked")) { 
			var value=$(this).val();
			value=value.substring(0,value.length-1);
		 	array.push(value);
                	falg += 1; 
			}	
		});  
		for (i in array){
			var array_text = JSON.stringify(array[i]);
			$.ajax({
				url:"/SystemStatus/MachineSet",
				type:"GET",
       	 		        data: {   sitename:"hust",
					  hostName: array_text,
                        	  	  flag: "reset" },
				dataType:"json",
			});
			alert("success");
		}
	}

	function PowerOn(){
	 	var array =new Array();
               	var falg=0;
               	$(".choose").each(function () {
        	       	if ($(this).attr("checked")) { 
			var value=$(this).val();
			value=value.substring(0,value.length-1);
		 	array.push(value);
                	falg += 1; 
			}	
		});  
		for (i in array){
			var array_text = JSON.stringify(array[i]);
			$.ajax({
				url:"/SystemStatus/MachineSet",
				type:"GET",
	       	 	        data: {   sitename:"hust",
					  hostName: array_text,
        	                  	  flag: "on" },
				dataType:"json",
				});
			alert("success");
		}
	}

        $("#selectall").click(chooseall);
     	function chooseall()
		{
			$(".choose").each(function () {
    				
					$(this).attr("checked",true);
 				}
				);
		}
     
	$("#unselectall").click(uchooseall);
     	
	function uchooseall(){
		$(".choose").each(function () {
			$(this).attr("checked",false);
 		});
	}
	
	function refreshDetails(){
		if (allsites.length==1){
			sitename=allsites[0];
		}
		else{
			sitename = $("#adminSystemStatusClusterNode").val();
		}
		console.log(sitename);	
		if ($("#hostmachine").is(":visible")){
			$('#adminSystemStatusHostTable').dataTable().fnClearTable();
			getHostsPoolInfo();
		}
		else{
			$('#adminSystemStatusVMTable').dataTable().fnClearTable();
			getVmsPoolInfo();
		}
	}

	$( "#systemHostInfo" ).accordion({
		fillSpace: true,
	});	
			
	$("#general_layout").addClass("activearea");
	$("#logview").hide();
	$("#hostmachine").hide();
	$("#hostsDetails").hide();
	$("#installmachine").hide();
	$("#clusterService").hide();
	
	$('#openchinamap').click(function(){
		$(".activearea").hide();
		$(".activearea").removeClass("activearea");
		$("#general_layout").addClass("activearea")		
		$(".activearea").show();
	});						
				
	$('#openmonitorpanel').click(function(){
		$(".activearea").hide();
		$(".activearea").removeClass("activearea");
		$("#hostsDetails").addClass("activearea")		
		$(".activearea").show();
		reDrawTables();
	});						

	$('#opentracepanel').click(function(){
		$(".activearea").hide();
		$(".activearea").removeClass("activearea");
		$("#traces").addClass("activearea")		
		$(".activearea").show();
		reDrawTables();
	});						

	$("#openlogpanel").click(function(){
		$(".activearea").hide();
		$(".activearea").removeClass();
		$("#logview").addClass("activearea");
		$(".activearea").show();
		reDrawTables();
		autoPullLogs();
		showLogPlot('action', 'Action Invoking -- Top 10');
		showLogPlot('site', 'Site Invoking')
	});

	$("#installation").click(function(){
		$(".activearea").hide();
		$(".activearea").removeClass("activearea");
		$("#installmachine").addClass("activearea");
		$(".activearea").show();
		reDrawTables();
		installGetinfo();
		
	});
	$("#refreshbutton").click(function(){
		$(".activearea").hide();
		$(".activearea").removeClass("activearea");
		$("#installmachine").addClass("activearea");
		$(".activearea").show();
		installGetinfo();
		
	});
	$("#adminSystemStatusClusterNode").change(
		refreshDetails
	);
	
	$("#adminSystemStatusNodeType").change( function(){
		var dest = $("#adminSystemStatusNodeType").val();
		if (dest=="vms"){
			$("#hostmachine").hide();
			$("#virtualmachine").show();
			refreshDetails();
		}else{
			$("#hostmachine").show();
			$("#virtualmachine").hide();
			refreshDetails();
		}
			
	} );
		
	$.plot($('#statusMonitorDetails'), []);

	$("#adminSystemStatusRefreshTableButton").click(function(event) {
		if (isHost)
			getHostsPoolInfo();
		else
			getVmsPoolInfo();
		resetVmStatusContainer();
		if (chart instanceof PerfChart) {
			chart.unsetRealTime();
			chart = null;
			$.plot($("#statusMonitorDetails"), []);
		}
	
	});

//////////////////////////////////////////////////////////////////////////////////////
//
//			Initialize Section - Cluster Mapping
//
//
/*	var CLUSTER_LOCATION = {
		'hust':['华中科技大学','武汉'],
		'whu':['武汉大学','武汉'],
		'ccnu':['华中师范大学','武汉'],
		'tsu':['清华大学','北京'],
		'pku':['北京大学','北京'],
		'buaa':['北京航空航天大学','北京'],
		'ruc':['中国人民大学','北京'],
		'bnu':['北京师范大学','北京'],
		'bupt':['北京邮电大学','北京'],
		'bstb':['北京科技大学','北京'],
		'but':['北京工业大学','北京'],
		'buct':['北京化工大学','北京'],
                'upc':['中国石油大学','青岛'],
		'fdu':['复旦大学','上海'],
		'sjtu':['上海交通大学','上海'],
		'sjtu2':['上海交通大学-2','上海'],
		'tju':['同济大学','上海'],
		'shu':['上海大学','上海'],
		'cqu':['重庆大学','重庆'],
		'seu':['东南大学','南京'],
		'hhu':['河海大学','南京'],
		'ouc':['中国海洋大学','青岛'],
		'xjtu':['西安交通大学','西安'],
		'xjtu2':['西安交通大学-2','西安'],
		'nwpu':['西北工业大学','西安'],
		'nudt':['国防科技大学','长沙'],
		'csu':['中南大学','长沙'],
		'hnu':['湖南大学','长沙'],
		'jlu':['吉林大学','长春'],
		'neu':['东北大学','沈阳'],
		'dlmu':['大连海事大学','大连'],
		'dlut':['大连理工大学','大连'],
		'hrbeu':['哈尔滨工程大学','哈尔滨'],
		'sdu':['山东大学','济南'],
		'zju':['浙江大学','杭州'],
		'hdu':['杭州电子科技大学','杭州'],
		'xju':['新疆大学','乌鲁木齐'],
		'sysu':['中山大学','广州'],
                'sysu2':['中山大学-2','广州'],
		'scut':['华南理工大学','广州'],
		'ustc':['中国科学技术大学','合肥'],
                'ustc2':['中国科学技术大学-2','合肥'],
		'hfut':['合肥工业大学','合肥'],
		'ynu':['云南大学','昆明'],
		'uestc':['电子科技大学','成都'],
		'lzu':['兰州大学','兰州'],
                'ncut':['北方工业大学','北京'],
                'tjmu':['华中科技大学同济医学院','武汉'],
		'hfut':['合肥工业大学','合肥'],
		'test':['crane09测试节点','测试节点']
	};

	$.ajax({
		url:"/ClusterNodes/getClusterNodesInfo",
		type:"GET",
		data:{},
		dataType:"json",
		timeout:40000,
		success:function(data){
			datanew = eval(data);
			$("#hostDetails").data("info", datanew);
			if (allsites.length!=1){
				for (var key in datanew) {
					if (datanew[key].Status=="ON"){
						$(".select_site").append("<option value='"+key+"'>"+CLUSTER_LOCATION[key][0]+"</option>");
					}
				}
				sitename = $("#adminSystemStatusClusterNode").val();
			}
			else{
				sitename=allsites[0];
			}
			getVmsPoolInfo();
			$("#clusterService").data("info",data);
                        loadClusterTable(data);
		}
	});*/
	
	bindEvents();



//////////////////////////////////////////////////////////////////////////////
//														
//			Initialize Section - Logs & Statistics
//
//

	////////////////  Logs Display  /////////////////
	$("#log_content").data('end', -query_log_num);

	function autoPullLogs(){
		$.ajax({
			url: "/ClusterNodes/queryLogsById",
			type: "GET",
			data: { start: $("#log_content").data('end') },
			dataType: "json",
			timeout: 30000,
			success: function(data) {
				var log = null;
				data = eval(data);
				console.log(data);
				if (data[0]) {
					var key = 0;
					var effect_time = data[1].length>20 ? [50, 200]: [800, 1000];
					var record_num = $(".log_content_body > div").size();
					console.log(record_num);
					function addOneRecord() {
						if (key<data[1].length) {
							log = data[1][key++]; 
							$("<div><table><tr><td>"+log.id+"</td><td>"+log.user+"</td><td>"+log.action+"</td><td>"+log.site+"</td><td>"+log.arr_time+"</td><td>"+log.lea_time+"</td><td>"+(log.ret?'Success':'failed')+"</td></tr><table></div>").prependTo($(".log_content_body")).fadeIn(effect_time[1]);
							setTimeout(addOneRecord, effect_time[0]);
						} else {
							if (log!=null)
								$("#log_content").data('end', log.id);
						}
					}
					addOneRecord();
					// If first query logs, we do 
					if (record_num==0)
						$("#log_content").data('start', data[1][0].id);
						setTimeout(function(){ $("#btn_earlier").show() }, 1000);
				}
				if ($("#log_content").is(":visible"))
					setTimeout(autoPullLogs, 30000);
			}
		});
	}

	function queryEarlierLogs(){
		$.ajax({
			url: "/ClusterNodes/queryLogsById",
			type: "GET",
			data: { start: $("#log_content").data('start')-query_log_num-1 > 0 ? $("#log_content").data('start')-query_log_num-1 : 0,
				end: $("#log_content").data('start') },
			dataType: "json",
			timeout: 3000,
			success: function(data) {
				var log = null;
				data = eval(data);
				console.log(data);
				if (data[0]) {
					var key = data[1].length-1;
					var effect_time = data[1].length>20 ? [50, 80] : [800, 1000];
					var record_num = $("#.log_content_body > div").size();
					$("#btn_earlier").fadeOut();
					function appendOneRecord() {
						if (key>=0) {
							log = data[1][key--]; 
							$("<div><table><tr><td>"+log.id+"</td><td>"+log.user+"</td><td>"+log.action+"</td><td>"+log.site+"</td><td>"+log.arr_time+"</td><td>"+log.lea_time+"</td><td>"+(log.ret?'Success':'Failed')+"</td></tr><table></div>").appendTo($(".log_content_body")).fadeIn(effect_time[1]);
							setTimeout(appendOneRecord, effect_time[0]);
						} else {
							if (log!=null)
								$("#log_content").data('start', log.id);
								if (log.id>1)
									$("#btn_earlier").fadeIn(1000);
						}
					}
					appendOneRecord()
				}
			}
		});
	}
	
	$("#btn_earlier").click(queryEarlierLogs);
	/////////////////  Logs Statistics  ///////////////
	function showLogPlot(cate, tit) {
		$.ajax({
			url: "/ClusterNodes/queryCategoryCount",
			type: "GET",
			data: { group: cate,
				num: 10 },
			dataType: "json",
			timeout: 3000,
			success: function(data) {
				data = eval(data);
				if (data[0]) {
					plotList[cate] = $.jqplot (cate+'_plot', [data[1]], {
						title: {
							text: tit,
							show: true
						},
						seriesDefaults: {
							renderer: jQuery.jqplot.PieRenderer,
							rendererOptions: {
								sliceMargin: 1,
								showDataLabels: true
							}
						},
						legend: {show: true, location: 'w'}
					});
					$("#"+cate+"_plot").bind("jqplotDataHighlight", function(evt, ser_index, pot_index, data){
						$(".float_panel").html("<div>"+data[0]+"</div><div>Count:"+data[1]+"</div>").fadeIn(500);
					}).bind("jqplotDataUnhighlight", function(evt, ser_index, pot_index, data){
						$(".float_panel").fadeOut(500);
					}).bind("jqplotDataMouseOver", function(evt, ser_index, pot_index, data){
						console.log(evt);
						$(".float_panel").css('left',evt.pageX);
						$(".float_panel").css('top', evt.pageY);
					});
				}
			}
		});
	}

	///////////////  Switch between LogsDisplay and LogsStatistics ///////////////
	//Next Button
	$("#btn_right").click(function(){
		if ($("#log_window > div:last").css('left') != '0px'){
			$("#log_window > div").animate({left:'-=1000px'}, 500);
		}
	}).mouseenter(function(e){
		if ($("#log_window > div:last").css('left') != '0px')
			$(this).fadeTo(500, 0.9);
	}).mouseleave(function(e){
		$(this).fadeTo(500, 0.1);
	});
	//Previous Button
	$("#btn_left").click(function(e){
		if ($("#log_window > div:first").css('left') != '0px'){
			$("#log_window > div").animate({left:'+=1000px'}, 500);
		}
	}).mouseenter(function(e){
		if ($("#log_window > div:first").css('left') != '0px')
			$(this).fadeTo(500, 0.9);
	}).mouseleave(function(e){
		$(this).fadeTo(500, 0.1);
	});

	setTimeout(refreshDetails, 1000);

	
});


