$(document).ready(function(){

/////////// Open & Close General Layout ////////////////////
	$("#btn_gen_layout").click(function(){
		$("body").css('overflow', 'hidden');
		$(".blackmask, #general_layout").fadeIn();
	});
	$(".blackmask > .btn_close").click(function(){
		$(".blackmask, #general_layout").fadeOut(function(){
			$("body").css('overflow', 'scroll');
		});
	});


///////////// Initialize Cluster Map ////////////

	var CLUSTER_LEVEL = [
		{radius: 2, color: 'grey'}, 
		{radius: 3, color: '#ff0000'},
		{radius: 2.5, color: '#dd0022'},
		{radius: 2, color: '#cc0033'},
		{radius: 2, color: '#ff0000'}
	];

	var CLUSTER_LOCATION = {
		'hust':['华中科技大学','武汉', 'hubei'],
		'whu':['武汉大学','武汉', 'hubei'],
		'ccnu':['华中师范大学','武汉', 'hubei'],
		'tsu':['清华大学','北京', 'beijing'],
		'pku':['北京大学','北京', 'beijing'],
		'buaa':['北京航空航天大学','北京', 'beijing'],
		'ruc':['中国人民大学','北京', 'beijing'],
		'bnu':['北京师范大学','北京', 'beijing'],
		'bupt':['北京邮电大学','北京', 'beijing'],
		'bstb':['北京科技大学','北京', 'beijing'],
		'but':['北京工业大学','北京', 'beijing'],
		'buct':['北京化工大学','北京', 'beijing'],
                'upc':['中国石油大学','青岛'],
		'fdu':['复旦大学','上海', 'shanghai'],
		'sjtu':['上海交通大学','上海', 'shanghai'],
		'sjtu2':['上海交通大学-2','上海', 'shanghai'],
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

	function onClickCluster() {
		if ($("#details").css("left")=="400px")
			$("#detailview_2").trigger("click");
		var selected = $(this).attr("id").split("_")[1];
		var info = $("#chinamap").data("info")[selected];
		
		setTimeout(function(){
			$("#clusterName .detail_content").addClass("helix");
			setTimeout(function(){
				$("#clusterName .detail_content").empty();
				$("#clusterName .detail_content").text(selected);
				$("#clusterName .detail_content").removeClass("helix");
			}, 300);
		}, 0);
		
		setTimeout(function(){
			$("#clusterSchool .detail_content").addClass("helix");
			setTimeout(function(){
				$("#clusterSchool .detail_content").empty();
				$("#clusterSchool .detail_content").text(CLUSTER_LOCATION[selected][0]);
				$("#clusterSchool .detail_content").removeClass("helix");
			}, 300);
		}, 0);
		
		setTimeout(function(){
			$("#clusterStatus .detail_content").addClass("helix");
			setTimeout(function(){
				$("#clusterStatus .detail_content").empty();
				$("#clusterStatus .detail_content").text(info.Status);
				$("#clusterStatus .detail_content").removeClass("helix");
			}, 300);
		}, 0);
		
		setTimeout(function(){
			$("#clusterHosts .detail_content").addClass("helix");
			setTimeout(function(){
				$("#clusterHosts .detail_content").empty();
				$("#clusterHosts .detail_content").text(info.Hosts);
				$("#clusterHosts .detail_content").removeClass("helix");
			}, 300);
		}, 0);
		
		setTimeout(function(){
			$("#clusterCPU .detail_content").addClass("helix");
			setTimeout(function(){
				$("#clusterCPU .detail_content").empty();
				$("#clusterCPU .detail_content").text(info.CPUTotal);
				$("#clusterCPU .detail_content").removeClass("helix");
			}, 300);
		}, 0);
		
		setTimeout(function(){
			$("#clusterUsers .detail_content").addClass("helix");
			setTimeout(function(){
				$("#clusterUsers .detail_content").empty();
				$("#clusterUsers .detail_content").text(info.UsersTotal);
				$("#clusterUsers .detail_content").removeClass("helix");
			}, 300);
		}, 0);
		
		setTimeout(function(){
			$("#clusterJobs .detail_content").addClass("helix");
			setTimeout(function(){
				$("#clusterJobs .detail_content").empty();
				$("#clusterJobs .detail_content").text(info.JobsRunning);
				$("#clusterJobs .detail_content").removeClass("helix");
			}, 300);
		}, 0);
	
		var num;
		setTimeout(function(){
			$("#clusterMem .detail_content").addClass("helix");
			setTimeout(function(){
				$("#clusterMem .detail_content").empty();
				if (info.Status=="ON") {
					num = parseInt(info.MemTotal)/1024/1024;
					$("#clusterMem .detail_content").text(num.toFixed(2)+" GB");
				}
				$("#clusterMem .detail_content").removeClass("helix");
			}, 300);
		}, 0);

		setTimeout(function(){
			$("#clusterMemUsage .detail_content").addClass("helix");
			setTimeout(function(){
				$("#clusterMemUsage .detail_content").empty();
				if (info.Status=="ON"){
					num = parseInt(info.MemUsed)/parseInt(info.MemTotal)*100;
					$("#clusterMemUsage .detail_content").text(num.toFixed(2)+" %");
				}
				$("#clusterMemUsage .detail_content").removeClass("helix");
			}, 300);
		}, 0);

		setTimeout(function(){
			$("#clusterCPUUsage .detail_content").addClass("helix");
			setTimeout(function(){
				$("#clusterCPUUsage .detail_content").empty();
				if (info.Status=="ON") {
					num = parseInt(info.CPUUsed)/parseInt(info.CPUTotal)*100;
					$("#clusterCPUUsage .detail_content").text(num.toFixed(2)+" %");
				}
				$("#clusterCPUUsage .detail_content").removeClass("helix");
			}, 300);
		}, 0);
	
		setTimeout(function(){
			$("#clusterStorage .detail_content").addClass("helix");
			setTimeout(function(){
				$("#clusterStorage .detail_content").empty();
				if (info.Status=="ON"){
					num = parseInt(info.DiskTotal)/1024/1024;
					$("#clusterStorage .detail_content").text(num.toFixed(2)+" GB");
				}
				$("#clusterStorage .detail_content").removeClass("helix");
			}, 300);
		}, 0);				


	}

	function clusterBlink(obj, time) {
		/*$("#"+obj).fadeIn(time, function(){
			clusterBlink(obj, Math.random()*4000+1000);
		});*/
		setInterval(function(){
			$("#"+obj).animate({opacity:"0"}, 50, 'swing', function(){$("#"+obj).animate({opacity:"1"}, 1500)});
			},1600);	
		
	}

	function generateRect(obj, num){
		var x0, y0, x, y;
		var rect;
		var svg = document.getElementsByTagName("svg")[0];
		var first_circle = document.getElementsByTagName("circle")[0];
		x0 = parseInt($("#node_"+obj).attr('cx'));
		y0 = parseInt($("#node_"+obj).attr('cy'));
		for (var i=0; i<num/3; i++){
			x = x0 + (CLUSTER_LOCATION[obj][1]=='上海'||CLUSTER_LOCATION[obj][1]=='青岛' ? -parseInt(Math.random()*10) : parseInt(Math.random()*20)-10);
			y = y0 + (CLUSTER_LOCATION[obj][1]=='大连'||CLUSTER_LOCATION[obj][1]=='广州' ? -parseInt(Math.random()*10) : parseInt(Math.random()*20)-10);
			rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
			rect.setAttributeNS(null, "id", obj+i);
			rect.setAttributeNS(null, "width", 1.3);
			rect.setAttributeNS(null, "height", 1.3);
			rect.setAttributeNS(null, "x", x);
			rect.setAttributeNS(null, "y", y);
			rect.setAttributeNS(null, "style", "fill:#cc3300");
			svg.insertBefore(rect, first_circle);
		}
	}

	function totalAmount(data) {
		var totalClusters = 0;
		var totalAvailable = 0;
		var totalHosts = 0;
		var totalCPU = 0;
		var totalMem = 0;
		var totalStorage = 0;
		var totalUsers = 0;
		var totalJobs = 0;
		for (var key in data) {
			var node = data[key];
			totalClusters++;
			if (node.Status=="ON"){
				totalAvailable++;
				totalHosts += node.Hosts;
				totalCPU += node.CPUTotal;
				totalMem += node.MemTotal;
				totalStorage += node.DiskTotal;
				totalUsers += node.UsersTotal;
				totalJobs += node.JobsRunning;
			}
		}
		var num;
		$("#generalCluster .detail_content").text(totalClusters);
		$("#generalAvailable .detail_content").text(totalAvailable);
		$("#generalHosts .detail_content").text(totalHosts);
		$("#generalCPU .detail_content").text(totalCPU);
		$("#generalMem .detail_content").text(totalMem);
		num = parseInt(totalMem)/1024/1024;
		$("#generalMem .detail_content").text(num.toFixed(2)+" GB");
		num = parseInt(totalStorage)/1024/1024;
		$("#generalStorage .detail_content").text(num.toFixed(2)+" GB");
		$("#generalUsers .detail_content").text(totalUsers);
		$("#generalJobs .detail_content").text(totalJobs);
	}	
		
	$.ajax({
		url: "/ClusterNodes/getClusterNodesinfoCache",
		type: "GET",
		data: {},
		dataType: "json",
		timeout: 30000,
		success: function(data){
			data = eval(data);
			$("#chinamap").data("info", data);
			console.log(data);	
			
			for (var key in CLUSTER_LOCATION){
				if (data[key]!=null){
					var node = data[key];
					console.log(key);
					console.log(node);
					switch (node.Status){
						case "ON":
							if(! node.Level){
								node.Level = 2;
							}
							$("#node_"+key).attr('r', CLUSTER_LEVEL[node.Level].radius);
							$("#node_"+key).attr('fill', CLUSTER_LEVEL[node.Level].color);			
							clusterBlink('node_'+key, 500);			
							$(".select_site").append("<option value='"+key+"'>"+CLUSTER_LOCATION[key][0]+"</option>");
							//generateRect(key, data[key].JobsRunning);
							break;
						case "OFF":
							$("#node_"+key).attr('r', CLUSTER_LEVEL[node.Level].radius);
							$("#node_"+key).attr('fill', CLUSTER_LEVEL[node.Level].color);			
							break;
						case "PENDING":
							$("#node_"+key).attr('r', CLUSTER_LEVEL[4].radius);
							$("#node_"+key).attr('fill', CLUSTER_LEVEL[4].color);
							break;
					}
				}else{
					$("#node_"+key).attr('r', CLUSTER_LEVEL[0].radius);
					$("#node_"+key).attr('fill', CLUSTER_LEVEL[0].color);
					var infos = $("#chinamap").data("info");
					infos[key] = {};
					$("#chinamap").data("info", infos);
				}
				$("#node_"+key).click(onClickCluster);

			}

			totalAmount(data);
		},
		error: function(XMLHttpRequest, textStatus, errorThrown){
			if ("timeout" == textStatus){ 
				var data = {}
				for (var key in CLUSTER_LOCATION){
					$("#node_"+key).attr('r', CLUSTER_LEVEL[0].radius);
					$("#node_"+key).attr('fill', CLUSTER_LEVEL[0].color);
					data[key] = {"Status":"OFF"};
				}
				$("#chinamap").data("info", data);
				$("#node_"+key).click(onClickCluster);
			}
		}
	});

	$("#detailview_1").click(function(){
		if ($("#generals").css("left")!='0px')
			$("#detail_container > div").animate({left: "+=400px"}, 200);
			$("#detailview_1").css('background-color', '#f1f1f1');
			$("#detailview_2").css('background-color', '#a0a0a0');
	});
	$("#detailview_2").click(function(){
		if ($("#details").css("left")!='0px')
			$("#detail_container > div").animate({left: "-=400px"}, 200);
			$("#detailview_2").css('background-color', '#f1f1f1');
			$("#detailview_1").css('background-color', '#a0a0a0');
	});

});

