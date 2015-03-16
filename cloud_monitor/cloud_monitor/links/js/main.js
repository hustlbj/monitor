$(document).ready(function() {

	var currenttab = 0;
	var prevtab = 0;
	var toggleflag = 0;

	$(".a2button ").button();
	$(".a2button ").css("font-size", "0.8em");
	$(".myarea-body .a2button ").css("font-size", "0.9em");
	$(".float-div .a2button ").css("font-size", "0.9em");

	$(".myarea-head").corner("top");
	$(".myarea-body").corner("bottom");

	$("input[type=\"text\"]").click(function() {
		$(this).val('');
	});

	$("#commonUserManage").click(function() {
		$(".float-div-back").show();
		$("#user_manage").show(1000);
		document.getElementById("serviceType").length = 0;
		getServiceName();
		getUserInfo();
		$.post('/UserManage/responseForUser', function(serverResponse) {
			document.getElementById("responseNumber").innerHTML = serverResponse[1].length;
			responseforuser = serverResponse;
		}, 'json');
	})

	$("#userManage").click(function() {
		$(".admin-float-div-back").show();
		$("#admin_user_manage").show(1000);
		getUserName(userload);
		$.post('/UserManage/adminRequest', {
		}, function(serverResponse) {
			document.getElementById("requestNumber").innerHTML = serverResponse[1].length;
		}, 'json');

	});

	$(".closeAdminFloatUserManage").click(function() {
		$(".admin-float-div-back").hide();
		$("#notice").hide();
		$(".usermanage_more").hide(500);
		$("#admin_user_manage").hide(500);
	});

	$(".closeAdminFloatContent").click(function() {
		$("#notice").hide();
		$(".usermanage_more").hide(500);
		$("#admin_user_manage").show(1000);
	});

	$(".closeFloatUserManage").click(function() {
		$(".float-div-back").hide();
		$("#user_manage").hide();
		$(".usermanage_more").hide(500);
	})
	$(".closeFloatContent").click(function() {
		$(".usermanage_more").hide(500);
		$("#user_manage").show(500);
	})

	$("#positive").click(function() {
		var userName = $("#user").val();
		var tenement = $("#tenement").val().substring(0, $("#tenement").val().indexOf('('));
		var serviceName = $("#adminServiceType").val();
		$.post('/UserManage/adjustUserTenement', {
			userName : userName,
			serviceName : serviceName,
			tenement : tenement
		}, function(serverResponse) {
			alert(serverResponse);
		}, 'json');
		$("#notice").hide();
		$(".admin-float-div-back").hide();
		$(".usermanage_more").hide();
	});

	$("#notive").click(function() {
		document.getElementById("notice").style.display = "None";
		//	$(".admin-float-div-back").hide();
		//	$("#modifyTenement_content").hide();
	});

	$("#positive_resource").click(function() {
		var serviceName = $("#service_resource").val();
		var resourceName = $("#resource").val().split(",")[0];
		rt = $.ajax({
			url : "/UserManage/getAllTenementLevel",
			data : {
				serviceName : serviceName
			},
			async : false,
			dataType : 'json'
		}).responseText;
		rt = eval('(' + rt + ')');
                var resourceValue=[];
                if(rt&&rt[0]==true){
                var flag=0;
                for(var i=0;i<rt[1].length;i++){
                    if($("#resourcevalue"+i).val()==""){
                        document.getElementById("error_02").innerHTML="请输入对应的值";
                        flag=1;
                    }

                    else if((/[0-9]/.test($("#resourcevalue"+i).val()))==false){
                        document.getElementById("error_02").innerHTML="请输入数字";
                        flag=1;
                    }else{
                      resourceValue[i]=$("#resourcevalue"+i).val();
                    }
                 }
                    if(flag==0){
                        document.getElementById("error_02").innerHTML="";
			$.post('/UserManage/adjustTenementResourceByResourceName', {
				serviceName : serviceName,
				resourceName : resourceName,
				ResourceValue : JSON.stringify(resourceValue)
			}, function(serverResponse) {
				alert(serverResponse);
			}, 'json');
			$("#notice_resource").hide();
			$(".admin-float-div-back").hide();
			$(".usermanage_more").hide();
                   }
               }
	});

	$("#notive_resource").click(function() {
		$("#notice_resource").hide();
		//	$(".admin-float-div-back").hide();
		//	$("#modifyResource_content").hide();
	});

	$("#positive_api").click(function() {
		var service = $("#service_api").val();
		var value = $("#tenement-apilevel").val();
                $("#notice_api").hide();
                $("#notice_api_init").show();
		if (value==""||value=="输入要修改的级别值") {
			document.getElementById("error_03").innerHTML = "请输入对应的级别值";
		} else {
			apiName = $("#api_level").val().split(",")[0];
			$.post('/UserManage/adjustLevelByApiName', {
				serviceName : service,
				apiName : apiName,
				level : value
			}, function(serverResponse) {
				alert(serverResponse);
			}, 'json');
			$(".admin-float-div-back").hide();
			$(".usermanage_more").hide();
		}
	});

	$("#notive_api").click(function() {
		$("#notice_api").hide();
		//	$(".admin-float-div-back").hide();
		//	$("#modifyApi_content").hide();
	});

	$("#positive_tenement_update").click(function() {
		var service = $("#service_tenement_update").val();
		var tenement = $("#tenement_update").val().substring(0, $("#tenement_update").val().indexOf('('));
		var value = $("#tenement-level-update").val();
		if (value==""||value=="输入要修改的基本值") {
			$("#notice_tenement_api").hide();
			document.getElementById("error_07").innerHTML = "输入对应的级别值";
		} else {
			$.post('/UserManage/adjustLevelByTenement', {
				serviceName : service,
				tenement : tenement,
				level : value
			}, function(serverResponse) {
				alert(serverResponse);
			}, 'json');
			$("#notice_tenement_api").hide();
			$(".admin-float-div-back").hide();
			$(".usermanage_more").hide();
		}
	});

	$("#notive_tenement_update").click(function() {
		$("#notice_tenement_api").hide();
	});

	$("#positive_tenement_add").click(function() {
		var serviceName = $("#service_tenement_add").val();
		var tenement =$("#tenement-level-addname").val(); 
		var level = $("#tenement-level-addvalue").val();
                 document.getElementById("error_04").innerHTML = "";
		if (serviceName=="")
                       document.getElementById("error_04").innerHTML = "请选择服务名";
                else if(tenement=="")
                       document.getElementById("error_04").innerHTML = "请输入对应的租户名";
                else if(level==""){
		       document.getElementById("error_04").innerHTML = "请输入对应的租户级别值";
		} else {
			$.post('/UserManage/newTenementToService', {
				serviceName : serviceName,
				tenement : tenement,
				level : level
			}, function(serverResponse) {
				alert(serverResponse);
			}, 'json');
			$(".admin-float-div-back").hide();
			$(".usermanage_more").hide();
		}
	});

	$("#notive_tenement_add").click(function() {
		$("#notice_tenement_add").hide();
		//	$(".admin-float-div-back").hide();
		//	$("#addTenement_content").hide();
	});

        $("#positive_addNewService").click(function() {
                serviceName=$("#newService_select").val();
                tenement=$("#newService_tenement").val().substring(0,$("#newService_tenement").val().indexOf("("));
                $.post('/UserManage/addServiceForUser', {
                        serviceName : serviceName,
                        userName:adminuserName,
                        tenement:tenement
                }, function(serverResponse) {
                                alert(serverResponse);
                        }, 'json');  
                $("#addNewService_more").hide();
                $(".admin-float-div-back").hide();
                $(".usermanage_more").hide(); 
        });
        
        $("#notive_addNewService").click(function() {
                $("#notice_addNewService").hide();
        });

	$("#positive_tenement_delete").click(function() {
		var serviceName = $("#service_tenement_delete").val();
		var tenement = $("#tenement_delete").val().substring(0, $("#tenement_delete").val().indexOf('('));
		$.post('/UserManage/deleteTenementFromService', {
			serviceName : serviceName,
			tenement : tenement
		}, function(serverResponse) {
			alert(serverResponse);
		}, 'json');
		$("#notice_tenement_delete").hide();
		$(".admin-float-div-back").hide();
		$(".usermanage_more").hide();
	});

	$("#notive_tenement_delete").click(function() {
		$("#notice_tenement_delete").hide();
		//	$(".admin-float-div-back").hide();
		//	$("#deleteTenement_content").hide();
	});

	$("#positive_api_add").click(function() {
		var service = $("#service_api_add").val();
		var apiName = $("#api-level-addname").val();
		var level = $("#api-level-addvalue").val();
		if (apiName=="")
                   document.getElementById("error_05").innerHTML = "请输入对应的API名";
                else if(level=="")
                   document.getElementById("error_05").innerHTML = "请输入对应的级别值";
		else {
			$.post('/UserManage/insertApiNameLevel', {
				serviceName : service,
				apiName : apiName,
				level : level
			}, function(serverResponse) {
				alert(serverResponse);
			}, 'json');
			$(".admin-float-div-back").hide();
			$(".usermanage_more").hide();
		}
	});


	$("#positive_resource_add").click(function() {
		var service = $("#service_Resource_add").val();
		var resourceName = $("#resourceName").val();
	        var chinese = $("#resourceNameChinese").val();
                var unit = $("#Unit").val();
		var ResourceTemenentDict = {};
		var rt = $.ajax({
			url : "/UserManage/getAllTenementLevel",
			data : {
				serviceName : service
			},
			async : false,
			dataType : 'json'
		}).responseText;
		rt = eval('(' + rt + ')');
		if (service==""){
			document.getElementById("error_06").innerHTML = "请选择服务名";
		}
                else if(resourceName==""){
                        document.getElementById("error_06").innerHTML = "请输入资源名英文值";
                }
                else if(chinese==""){
                        document.getElementById("error_06").innerHTML = "请输入资源名中文值";
                }
                 else if(unit==""){
                         document.getElementById("error_06").innerHTML = "请输入单位名";
                }
                else {
			for (var i = 0; i < rt[1].length; i++) {
				ResourceTemenentDict[rt[1][i][0]] =$("#"+"resourcevalue"+i).val();
			}
			$.post('/UserManage/insertResource', {
				serviceName : service,
				resourceName : resourceName,
				ChineseName : chinese,
				unit : unit,
				ResourceTemenentDict : JSON.stringify(ResourceTemenentDict)
			}, function(serverResponse) {
				alert(serverResponse);
			}, 'json');
			$(".admin-float-div-back").hide();
			$(".usermanage_more").hide();
		}
	});

	$("#notive_resource_add").click(function() {
		$("#notice_resource_add").hide();
		//	$(".admin-float-div-back").hide();
		//	$("#addResource_content").hide();
	});

	$("#editpsw").click(function() {
		$("#user_manage").hide();
		$("#adjustPassword").show(500);
		document.getElementById("password").value = "";
		document.getElementById("password2").value = "";
	});

	$("#positive_password").click(function() {
		var rt = $.ajax({
			url : "/UserManage/queryUserInfo",
			data : {
			},
			async : false,
			dataType : 'json'
		}).responseText;
		rt = eval('(' + rt + ')');
		userName = rt[0][0];
		password = document.getElementById("password").value;
		mailbox = rt[0][2];
		register = rt[0][3];
		$.post('/UserManage/adjustUserByUserName', {
			userName : userName,
			password : password,
			mailbox : mailbox,
			register : register
		}, function(serverResponse) {
			alert(serverResponse);
		}, 'json');
		$("#adjustPassword").hide();
		$(".float-div-back").hide();
	})

	$("#positive_api_delete").click(function() {
		var service = $("#service_api_delete").val();
		var apiName = $("#api_level_delete").val().split(",")[0];
		$.post('/UserManage/deleteLevelByApiName', {
			serviceName : service,
			apiName : apiName
		}, function(serverResponse) {
			alert(serverResponse);
		}, 'json');
		$("#notice_api_delete").hide();
		$(".admin-float-div-back").hide();
		$(".usermanage_more").hide();
	});

	$("#notive_api_delete").click(function() {
		$("#notice_api_delete").hide();
		//	$(".admin-float-div-back").hide();
		//	$("#deleteApi_content").hide();
	});

	$("#positive_resource_delete").click(function() {
		var service = $("#service_Resource_delete").val();
		var resourceName = $("#resource_level_delete").val().split(",")[0];
		$.post('/UserManage/deleteResourceByResourceName', {
			serviceName : service,
			resourceName : resourceName
		}, function(serverResponse) {
			alert(serverResponse);
		}, 'json');
		$("#notice_resource_delete").hide();
		$(".admin-float-div-back").hide();
		$(".usermanage_more").hide();
	});

	$("#notive_resource_delete").click(function() {
		$("#notice_resource_delete").hide();
		//	$(".admin-float-div-back").hide();
		//	$("#deleteResource_content").hide();
	});

	$("#positive_user_delete").click(function() {
		var userName = $("#user_logout").val();
		$.post('/UserManage/logout', {
			userName : userName
		}, function(serverResponse) {
			alert(serverResponse);
		}, 'json');
		$("#notice_user_logout").hide();
		$(".admin-float-div-back").hide();
		$(".usermanage_more").hide();
	});

	$("#notive_user_delete").click(function() {
		$("#notice_user_logout").hide();
		//	$(".admin-float-div-back").hide();
		//	$("#logout_content").hide();
	});

	$("#positive_tenement_to_be").click(function() {
		var userName = username;
		var serviceName = $("#service_tenement_type").val();
		var tenement = document.getElementById("tenementType").innerHTML;
		var tenementChange = document.getElementById("tenement_type_be").innerHTML;
		$.post('/UserManage/requestModifyTenement', {

			userName : userName,
			serviceName : serviceName,
			tenement : tenement,
			tenementChange : tenementChange
		}, function(serverResponse) {

			alert(serverResponse);

		}, 'json');
		$("#adjustTenement").hide();
		$(".user_manage").hide();
		$(".float-div-back").hide();
	});

	$("#notive_tenement_to_be").click(function() {
		$("#modify_tenement").hide();
		//	$(".usermanage_more").hide();
		//	$(".float-div-back").hide();
	});

	$("#notive_tenement_update").click(function() {
		$("#notice_tenement_api").hide();
	});

	$("#positive_newservice").click(function() {
		var serviceName = $("#newservice_type").val();
		$.post('/UserManage/requestAddUserService', {
			serviceName : serviceName
		}, function(serverResponse) {
			alert(serverResponse);
		}, 'json');
		$("#newServiceType_more").hide();
		$(".user_manage").hide();
		$(".float-div-back").hide();
	});

	$("#notive_newservice").click(function() {
		$("#newservice_more").hide();
	});

	$("#tenement").change(function() {
		var userName = $("#user").val();
		var tenementValue = $("#tenement").val();
		var tenement = tenementValue.substring(0, tenementValue.indexOf('('));
		document.getElementById("notice").style.display = "block";
		console.log(tenement);
		document.getElementById("user_more").innerHTML = userName;
		document.getElementById("tenement_more").innerHTML = tenement;
	});

	$("#user").change(function() {
		document.getElementById("error_01").innerHTML = "";
		var userName = $("#user").val();
                adminuserName=userName;
		document.getElementById("adminServiceType").length = 1;
		getServiceNameA(userName);
		getUserInfoA(userName);
	});

        $("#newService_select").change(function() {
                document.getElementById("newService_tenement").options.length=1;
                getAllTenementLevel("#newService_tenement", "#newService_select");   
        }); 

        $("#newService_tenement").change(function() {
                 $("#notice_addNewService").show();
                 document.getElementById("newService_select_more").innerHTML = $("#newService_select").val();
                 document.getElementById("newService_tenement_more").innerHTML = $("#newService_tenement").val().substring(0,$("#newService_tenement").val().indexOf("("));     
                 document.getElementById("addNewService_user").innerHTML = adminuserName;
        });

	$("#adminServiceType").change(function() {
		var userName = $("#user").val();
		if (userName == "choseUser") {
			document.getElementById("error_01").innerHTML = "请先选择用户名";
		} else {
                      //  $("#adminServiceType")[0].options.length = 0;
			var value = $("#adminServiceType").val();
			$('.activeservice').hide();
			$('.services').hide();
			document.getElementById(value).innerHTML = "";
			document.getElementById(value + '_service').innerHTML = "";
			$('#' + value).show(100);
			$('#' + value + '_service').show(100);
			$('.activeservice').removeClass();
			$('.services').removeClass();
			$('#' + value).addClass("activeservice");
			$('#' + value + '_service').addClass("services");
			var rt = $.ajax({
				url : "/UserManage/queryResourceOfUserA",
				data : {
					userName : userName,
					serviceName : value
				},
				async : false,
				dataType : 'json'
			}).responseText;
			rt = eval('(' + rt + ')');
			var titleDiv = document.createElement("h1");
			titleDiv.appendChild(document.createTextNode('服务资源配额' + '(' + userName + ':' + value + ')'));
			if (rt[0] == true) {
				var containerDiv = document.createElement("p");
				for (var key in rt[1]) {
					var contentDiv = document.createTextNode(key + ":" + rt[1][key]);
					containerDiv.appendChild(contentDiv);
					containerDiv.appendChild(document.createElement('br'));
					containerDiv.appendChild(document.createElement('br'));
				}
				document.getElementById(value).appendChild(titleDiv);
				document.getElementById(value).appendChild(document.createElement('br'));
				document.getElementById(value).appendChild(containerDiv);
			}

			var rt = $.ajax({
				url : "/UserManage/queryApiOfUserA",
				data : {
					userName : userName,
					serviceName : value
				},
				async : false,
				dataType : 'json'
			}).responseText;
			rt = eval('(' + rt + ')');
			if (rt[0] == true) {
				var titleDiv = document.createElement("ul");
				for (var key in rt[1]) {
					var containerDiv = document.createElement("li");
					var containerDivChild = document.createElement("a");
					containerDivChild.href = "#";
					var contentDiv = document.createTextNode(key + ":" + rt[1][key]);
					containerDivChild.appendChild(contentDiv);
					containerDiv.appendChild(containerDivChild);
					titleDiv.appendChild(containerDiv);
				}
				document.getElementById(value + '_service').appendChild(document.createElement('br'));
				document.getElementById(value + '_service').appendChild(titleDiv);
			}
		}
	});

	$("#serviceType").change(function() {
		var value = $("#serviceType").val();
		$('.activeservice').hide();
		$('.services').hide();
		$('#' + value).show(100);
		document.getElementById(value).innerHTML = "";
		document.getElementById(value + '_service').innerHTML = "";
		$('#' + value + '_service').show(100);
		$('.activeservice').removeClass();
		$('.services').removeClass();
		$('#' + value).addClass("activeservice");
		$('#' + value + '_service').addClass("services");
		$.post('/UserManage/queryResourceOfUser', {
			serviceName : value
		}, function(serverResponse) {
			result = serverResponse;
			var titleDiv = document.createElement("h1");
			titleDiv.appendChild(document.createTextNode('服务资源配额' + '(' + value + ')'));
			if (result && result[0] == true) {
				var containerDiv = document.createElement("p");
				for (var key in result[1]) {
					var contentDiv = document.createTextNode(key + ":" + result[1][key]);
					containerDiv.appendChild(contentDiv);
					containerDiv.appendChild(document.createElement('br'));
					containerDiv.appendChild(document.createElement('br'));
				}
				document.getElementById(value).appendChild(titleDiv);
				document.getElementById(value).appendChild(document.createElement('br'));
				document.getElementById(value).appendChild(containerDiv);
			}
		}, 'json');
		var rt = $.ajax({
			url : "/UserManage/queryApiOfUser",
			data : {
				serviceName : value
			},
			async : false,
			dataType : 'json'
		}).responseText;
		rt = eval('(' + rt + ')');
		if (rt[0] == true) {
			var titleDiv = document.createElement("ul");
			for (var key in rt[1]) {
				var containerDiv = document.createElement("li");
				var containerDivChild = document.createElement("a");
				containerDivChild.href = "#";
				var contentDiv = document.createTextNode(key + ":" + rt[1][key]);
				containerDivChild.appendChild(contentDiv);
				containerDiv.appendChild(containerDivChild);
				titleDiv.appendChild(containerDiv);
			}
			document.getElementById(value + '_service').appendChild(titleDiv);
		}

	});

	$("#getRequestInfo").click(function() {
		$("#admin_user_manage").hide(500);
		$("#requestInfo").show(500);
		$.post('/UserManage/adminRequest', {
		}, function(serverResponse) {
			if (serverResponse[0] == true) {
				var elemDiv = document.getElementById("requestInfo_detail");
				elemDiv.innerHTML = "";
				if (serverResponse[1].length == 0) {
					contentDiv = document.createElement("p");
					contentDiv.appendChild(document.createTextNode("暂时没有用户请求"));
					elemDiv.appendChild(contentDiv);
				} else {
					for (var i = 0; i < serverResponse[1].length; i++) {
						contentDiv = document.createElement("p");
						contentDiv.appendChild(document.createTextNode("No." + (i + 1)));
						contentSpan = document.createElement("span");
						if (serverResponse[1][i].length == 6) {
							contentSpan.appendChild(document.createTextNode("用户" + serverResponse[1][i][0] + "请求将服务" + serverResponse[1][i][4] + "的租户类型" + serverResponse[1][i][1] + "修改为" + serverResponse[1][i][2]));
						} else {
							contentSpan.appendChild(document.createTextNode("用户" + serverResponse[1][i][0] + "请求增加服务" + serverResponse[1][i][1]));
						}
						elemDiv.appendChild(contentDiv);
						elemDiv.appendChild(contentSpan);
					}
					elemDiv.appendChild(document.createElement("br"));
					elemDiv.appendChild(document.createElement("br"));
					contentDiv = document.createElement("a");
					contentDiv.href = "#";
					contentDiv.id = "deal_now";
					contentDiv.className = "read_more_more";
					contentDiv.appendChild(document.createTextNode("开始处理"));
					elemDiv.appendChild(contentDiv);
					$("#deal_now").click(function() {
						$("#requestInfo").hide();
						$("#admin_user_manage").show(500);
					});
				}
			}
		}, 'json');

	});

	$("#responseInfo").click(function() {
		$("#user_manage").hide(500);
		$("#responseInfo_more").show(500);
		if (responseforuser[0] == true) {
			var elemDiv = document.getElementById("responseInfo_more_detail");
			elemDiv.innerHTML = "";
			if (responseforuser[1].length == 0) {
				contentDiv = document.createElement("p");
				contentDiv.appendChild(document.createTextNode("Sorry,暂时还没有任何处理消息,如果您有申请修改租户类型的请求，请耐心等待"));
				elemDiv.appendChild(contentDiv);
			} else {
				for (var i = 0; i < responseforuser[1].length; i++) {
					contentDiv = document.createElement("p");
					if (responseforuser[1][i].length == 6) {
						contentDiv.appendChild(document.createTextNode("No." + (i + 1) + "您的请求:将服务" + responseforuser[1][i][4] + "的租户类型" + responseforuser[1][i][1] + "修改为" + responseforuser[1][i][2] + "已得到响应"));
					} else {
						contentDiv.appendChild(document.createTextNode("No." + (i + 1) + "您的请求:申请增加服务" + responseforuser[1][i][1] + "已得到响应"));
					}

					elemDiv.appendChild(contentDiv);
				}
			}
		}

	});

	$("#modifyTenement").click(function() {
		if ($("#user").val() == "" || $("#adminServiceType").val() == "服务类型") {
			document.getElementById("error_01").innerHTML = "(请选择用户名和服务类型)";
		} else {
			document.getElementById("error_01").innerHTML = "";
			$("#admin_user_manage").hide(500);
			$("#modifyTenement_content").show(500);
			document.getElementById("tenement").length = 1;
			document.getElementById("user-tenement").length = 1;
			getUserTenement("#user", "#adminServiceType", "user-tenement");
			getAllTenementLevel("#tenement", "#adminServiceType");
		}
	});

	$("#modifyResource").click(function() {
		$("#admin_user_manage").hide(500);
		$("#modifyResource_content").show(500);
		document.getElementById("error_02").innerHTML = "";
		document.getElementById("service_resource").length = 1;
		getAllService("#service_resource");
	});

	$("#modifyApi").click(function() {
		$("#admin_user_manage").hide(500);
		$("#modifyApi_content").show(500);
                $("#notice_api").hide();
                $(".notice_api_init").show();
		document.getElementById("error_03").innerHTML="";
		document.getElementById("service_api").length = 1;
		getAllService("#service_api");
	});

	$("#modifyServiceTenement").click(function() {
		$("#admin_user_manage").hide(500);
		$("#modifyServiceTenement_content").show(500);
		$("#notice_tenement_api").hide();
		$(".notice_tenement_api_init").show();
		document.getElementById("error_07").innerHTML="";
		document.getElementById("service_tenement_update").length = 1;
		getAllService("#service_tenement_update");
	});

	$("#addTenement").click(function() {
		$("#admin_user_manage").hide(500);
		$("#addTenement_content").show(500);
		document.getElementById("service_tenement_add").length = 1;
		getAllService("#service_tenement_add");
	});

	$("#deleteTenement").click(function() {
		$("#admin_user_manage").hide(500);
		$("#deleteTenement_content").show(500);
		document.getElementById("service_tenement_delete").length = 1;
		getAllService("#service_tenement_delete");
	});

	$("#addApi").click(function() {
		$("#admin_user_manage").hide(500);
		$("#addApi_content").show(500);
		document.getElementById("error_05").innerHTML = "";
		document.getElementById("service_api_add").length = 1;
		getAllService("#service_api_add");
	});

	$("#addResource").click(function() {
		$("#admin_user_manage").hide(500);
		$("#addResource_content").show(500);
		document.getElementById("service_Resource_add").length = 1;
		getAllService("#service_Resource_add");
	});

	$("#deleteApi").click(function() {
		$("#admin_user_manage").hide(500);
		$("#deleteApi_content").show(500);
		document.getElementById("service_api_delete").length = 1;
		getAllService("#service_api_delete");
	});

	$("#deleteResource").click(function() {
		$("#admin_user_manage").hide(500);
		$("#deleteResource_content").show(500);
		document.getElementById("service_Resource_delete").length = 1;
		getAllService("#service_Resource_delete");
	});

	$("#logoutUser").click(function() {
		$("#admin_user_manage").hide(500);
		$("#logout_content").show(500);
		getUserNameLogout(userloadLogout);
	});

	$("#modifyUserTenement").click(function() {
		$("#user_manage").hide(500);
		$("#adjustTenement").show(500);
		document.getElementById("service_tenement_type").length = 1;
		getServiceByUserName("#service_tenement_type");
	});

	$("#addNewService").click(function() {
                document.getElementById("admin_noNewService").style.display="None";
		$("#user_manage").hide(500);
		$("#addNewService_more").show(500);
                console.log($("#user").val());
		if ($("#user").val() == "") {
			document.getElementById("error_01").innerHTML = "(请选择用户名)";
		} else {
			document.getElementById("error_01").innerHTML = "";
			$("#admin_user_manage").hide(500);
			$("#addNewService_more").show(500);
			document.getElementById("newService_select").length = 1;
			var rt = $.ajax({
				url : "/UserManage/getAllService",
				data : {
				},
				async : false,
				dataType : 'json'
			}).responseText;
			rt = eval('(' + rt + ')');
			userName = $("#user").val();
			var rlt = $.ajax({
				url : "/UserManage/queryServiceNameA",
				data : {
					userName : userName
				},
				async : false,
				dataType : 'json'
			}).responseText;
			rlt = eval('(' + rlt + ')');
			var newArr = [];
			k = 0;
			for (var i = 0; i < rt.length; i++) {
				for ( j = 0; j < rlt[0].length; j++) {
					tmp = 1;
					if (rt[i] == rlt[0][j]) {
						tmp = 0;
						break;
					}
				}
				if (tmp == 1) {
					newArr[k] = rt[i];
					k++;
				}
			}
			if (newArr.length > 0) {
				var obj = $("#newService_select");
				obj.parent().children().remove("div");
				obj.removeClass();
				for (var i = 0; i < newArr.length; i++) {
					var name = new Option(newArr[i], newArr[i]);
					obj[0].options.add(name);
				}
				obj.addClass("chzn-select");
				$(".chzn-select").chosen();
			} else {
				var obj = $("#newService_select");
				obj.parent().children().remove("div");
				obj.removeClass();
				document.getElementById("admin_noNewService").style.display = "block";
				var obj = $("#newService_tenement");
				obj.parent().children().remove("div");
				obj.removeClass();
			}

		}
	});


	$("#newServiceType").click(function() {
		$("#user_manage").hide(500);
		$("#newServiceType_more").show(500);
		document.getElementById("newservice_type").length = 1;
		var rt = $.ajax({
			url : "/UserManage/getAllService",
			data : {
			},
			async : false,
			dataType : 'json'
		}).responseText;
		rt = eval('(' + rt + ')');

		var rlt = $.ajax({
			url : "/UserManage/queryServiceName",
			data : {
			},
			async : false,
			dataType : 'json'
		}).responseText;
		rlt = eval('(' + rlt + ')');
		var newArr = [];
		k = 0;
		for (var i = 0; i < rt.length; i++) {
			for ( j = 0; j < rlt[0].length; j++) {
				tmp = 1;
				if (rt[i] == rlt[0][j]) {
					tmp = 0;
					break;
				}
			}
			if (tmp == 1) {
				newArr[k] = rt[i];
				k++;
			}
		}
		if (newArr.length > 0) {
			var obj = $("#newservice_type");
			obj.parent().children().remove("div");
			obj.removeClass();
			for (var i = 0; i < newArr.length; i++) {
				var name = new Option(newArr[i], newArr[i]);
				obj[0].options.add(name);
			}
			obj.addClass("chzn-select");
			$(".chzn-select").chosen();
		} else {
			var obj = $("#newservice_type");
			obj.parent().children().remove("div");
			obj.removeClass();
			document.getElementById("noNewService").style.display = "block";
		}
	});

	$("#newservice_type").change(function() {
		var serviceName = $("#newservice_type").val();
		$("#newservice_more").show(500);
		document.getElementById("newservice_type_more").innerHTML = serviceName;

	});

	$("#service_tenement_type").change(function() {
		getUserTenementForUser("#service_tenement_type", "tenementType");
		document.getElementById("tenement_to_be").length = 1;
		getAllTenementLevel("#tenement_to_be", "#service_tenement_type");
	});

	$("#tenement_to_be").change(function() {
		$("#modify_tenement").show(500);
		document.getElementById("service_type_be_more").innerHTML = $("#service_tenement_type").val();
		document.getElementById("tenement_type_more").innerHTML = document.getElementById("tenementType").innerHTML;
		document.getElementById("tenement_type_be").innerHTML = $("#tenement_to_be").val().substring(0, $("#tenement_to_be").val().indexOf("("));

	});

	$("#user_logout").change(function() {
		var userName = $("#user_logout").val();
		document.getElementById("user_logout_more").innerHTML = userName;
		$("#notice_user_logout").show();
	});

        $("#service_resource").change(function(){
                document.getElementById("resource").length = 1;
                getResourceOfUser("#service_resource", "#resource");
        });

	$("#resource").change(function() {
		document.getElementById("service_tenement").innerHTML = "";
		getTenementForResource($("#service_resource").val());
                
	});
        function getTenementForResource(serviceName){
                 $.post('/UserManage/getAllTenementLevel',
                        {
                                serviceName : serviceName
                        },function(rlt){
                           if(rlt[0]==true){
                             var totalDiv = document.getElementById("service_tenement");
                                totalDiv.innerHTML="";
                             for(var i=0;i<rlt[1].length;i++){
                                totalP=document.createElement("span");
                                totalP.appendChild(document.createTextNode("*"+rlt[1][i]+"新资源值"));
                                totalP.style.display="-moz-inline-box";
                                totalP.style.display="inline-block";
                                totalP.style.width="210px";
                                totalDiv.appendChild(totalP);
				totalP1=document.createElement("input");
				totalP1.type="text";
				totalP1.id="resourcevalue"+i;
                                totalP1.style.width="100px";
                                totalDiv.appendChild(totalP1);
				totalDiv.appendChild(document.createElement('br'));
				totalDiv.appendChild(document.createElement('br'));
                             }
                           }       
                        },
                         'json'
                );
        }


	$("#service_Resource_add").change(function() {
		document.getElementById("service_resource_tenement").innerHTML = "";
                 getTenementForNewResource($("#service_Resource_add").val());
	});
        function getTenementForNewResource(serviceName){
                 $.post('/UserManage/getAllTenementLevel',
                        {
                                serviceName : serviceName
                        },function(rlt){
                           if(rlt[0]==true){
                             var totalDiv = document.getElementById("service_resource_tenement");
                                totalDiv.innerHTML="";
				totalP=document.createElement("span");
				totalP.appendChild(document.createTextNode("资源名英文值"));
				totalP.style.display="-moz-inline-box";
                                totalP.style.display="inline-block";
                                totalP.style.width="210px";
                                totalDiv.appendChild(totalP);
				totalP1=document.createElement("input");
                                totalP1.type="text";
                                totalP1.id="resourceName";
                                totalP1.style.width="100px";
                                totalDiv.appendChild(totalP1);
                                totalDiv.appendChild(document.createElement('br'));
                                totalDiv.appendChild(document.createElement('br'));
								
				totalPp=document.createElement("span");
				totalPp.appendChild(document.createTextNode("资源名中文值"));
				totalPp.style.display="-moz-inline-box";
                                totalPp.style.display="inline-block";
                                totalPp.style.width="210px";
                                totalDiv.appendChild(totalPp);
				totalPp1=document.createElement("input");
                                totalPp1.type="text";
                                totalPp1.id="resourceNameChinese";
                                totalPp1.style.width="100px";
                                totalDiv.appendChild(totalPp1);
                                totalDiv.appendChild(document.createElement('br'));
                                totalDiv.appendChild(document.createElement('br'));
								
			        totalPU=document.createElement("span");
				totalPU.appendChild(document.createTextNode("单位"));
				totalPU.style.display="-moz-inline-box";
                                totalPU.style.display="inline-block";
                                totalPU.style.width="210px";
                                totalDiv.appendChild(totalPU);
				totalPU1=document.createElement("input");
                                totalPU1.type="text";
                                totalPU1.id="Unit";
                                totalPU1.style.width="100px";
                                totalDiv.appendChild(totalPU1);
                                totalDiv.appendChild(document.createElement('br'));
                                totalDiv.appendChild(document.createElement('br'));							
                             for(var i=0;i<rlt[1].length;i++){
                                totalP=document.createElement("span");
                                totalP.appendChild(document.createTextNode("*"+rlt[1][i]+"对应租户的资源值"));
                                totalP.style.display="-moz-inline-box";
                                totalP.style.display="inline-block";
                                totalP.style.width="210px";
                                totalDiv.appendChild(totalP);
                                totalP1=document.createElement("input");
                                totalP1.type="text";
                                totalP1.id="resourcevalue"+i;
                                totalP1.style.width="100px";
                                totalDiv.appendChild(totalP1);
                                totalDiv.appendChild(document.createElement('br'));
                                totalDiv.appendChild(document.createElement('br'));
                             }
                           }
                        },
                         'json'
                );
        }

	$("#service_api").change(function() {
		document.getElementById("api_level").length = 1;
		getAllLevel("#service_api", "#api_level");
	});

	$("#service_tenement_update").change(function() {
		document.getElementById("tenement_update").length = 1;
		getAllTenementLevel("#tenement_update", "#service_tenement_update");
	});

	$("#service_api_delete").change(function() {
		document.getElementById("api_level_delete").length = 1;
		getAllLevel("#service_api_delete", "#api_level_delete");
	});

	$("#service_Resource_delete").change(function() {
		document.getElementById("resource_level_delete").length = 1;
		getResourceOfUser("#service_Resource_delete", "#resource_level_delete");
	});

	$("#resourcevalue").change(function() {
		var service = $("#service_resource").val();
		var resource = $("#resource").val().split(",")[0];
		var value = $("#resourcevalue").val();
		document.getElementById("service_resource_more").innerHTML = service;
		document.getElementById("resource_more").innerHTML = resource;
		document.getElementById("resourcevalue_more").innerHTML = value;
		$("#notice_resource").show(200);
	});

	$("#tenement-apilevel").change(function() {
		document.getElementById("error_03").innerHTML = "";
		var service = $("#service_api").val();
		var value = $("#tenement-apilevel").val();
		$("#notice_api").show();
		document.getElementById("service_api_more").innerHTML = service;
		document.getElementById("apilevel_more").innerHTML = value;
		document.getElementById("api_more").innerHTML = $("#api_level").val().split(",")[0];
		/*		if (valueArr[0] == 'A') {
		 document.getElementById("service_api_more").innerHTML = service;
		 document.getElementById("apilevel_more").innerHTML = valueArr[1];
		 document.getElementById("api_more").innerHTML = $("#tenement_api").val().substring(0, $("#tenement_api").val().indexOf("("));
		 } else if (valueArr[0] == 'B') {
		 $("#notice_api").show();
		 }*/
	})

	$("#tenement-level-update").change(function() {
		document.getElementById("error_07").innerHTML = "";
		var service = $("#service_tenement_update").val();
		var value = $("#tenement-level-update").val();
		$("#notice_tenement_api").show();
		document.getElementById("service_tenement_update_more").innerHTML = service;
		document.getElementById("tenement_update_more").innerHTML = $("#tenement_update").val().split(",")[0];
		document.getElementById("tenement_update_level_more").innerHTML = value;
	})


	$("#service_tenement_delete").change(function() {
		document.getElementById("tenement_delete").length = 1;
		getAllTenementLevel("#tenement_delete", "#service_tenement_delete");
	})

	$("#tenement_delete").change(function() {
		var service = $("#service_tenement_delete").val();
		var tenement = $("#tenement_delete").val().substring(0, $("#tenement_delete").val().indexOf('('));
		$("#notice_tenement_delete").show();
		document.getElementById("service_tenement_delete_more").innerHTML = service;
		document.getElementById("tenement_delete_more").innerHTML = tenement;
	})

	$("#resource-level-add").change(function() {
		var service = $("#service_Resource_add").val();
		var value = $("#resource-level-add").val();
		$("#notice_resource_add").show();
		document.getElementById("service_resource_add_more").innerHTML = service;
		document.getElementById("resource_add_more").innerHTML = value;
	});

	$("#api_level_delete").change(function() {
		var service = $("#service_api_delete").val();
		var value = $("#api_level_delete").val();
		$("#notice_api_delete").show();
		document.getElementById("service_api_delete_more").innerHTML = service;
		document.getElementById("api_delete_more").innerHTML = value;
	});

	$("#resource_level_delete").change(function() {
		var service = $("#service_Resource_delete").val();
		var value = $("#resource_level_delete").val();
		$("#notice_resource_delete").show();
		document.getElementById("service_resource_delete_more").innerHTML = service;
		document.getElementById("resource_delete_more").innerHTML = value;
	});

	function getAllLevel(serviceName, apiId) {
		var serviceName = $(serviceName).val();
		var rt = $.ajax({
			url : "/UserManage/getAllLevel",
			data : {
				serviceName : serviceName
			},
			async : false,
			dataType : 'json'
		}).responseText;
		rt = eval('(' + rt + ')');
		var obj = $(apiId);
		obj.parent().children().remove("div");
		obj.removeClass();
		if (rt[0] == true) {
			for (var i = 0; i < rt[1].length; i++) {
				var name = new Option(rt[1][i], rt[1][i]);
				$(apiId)[0].options.add(name);
			}
		}
		obj.addClass("chzn-select");
		$(".chzn-select").chosen();
	}

	function getAllService(serviceId) {
		var rt = $.ajax({
			url : "/UserManage/getAllService",
			data : {
			},
			async : false,
			dataType : 'json'
		}).responseText;
		var obj = $(serviceId);
		obj.parent().children().remove("div");
		obj.removeClass();
		rt = eval('(' + rt + ')');
		for (var i = 0; i < rt.length; i++) {
			var name = new Option(rt[i], rt[i]);
			$(serviceId)[0].options.add(name);
		}
		obj.addClass("chzn-select");
		$(".chzn-select").chosen();
	}

        function getServiceByUserName(serviceId){
         var rt = $.ajax({
                        url : "/UserManage/queryServiceName",
                        data : {
                        },
                        async : false,
                        dataType : 'json'
                }).responseText;
                rt = eval('(' + rt + ')');
                var obj = $(serviceId);
                obj.parent().children().remove("div");
                obj.removeClass();
                for (var i = 0; i < rt[0].length; i++) {
                        var name = new Option(rt[0][i], rt[0][i]);
                        $(serviceId)[0].options.add(name);
                }
                obj.addClass("chzn-select");
                $(".chzn-select").chosen();
        }

	function getResourceOfUser(serviceName, resourceId) {
		var serviceName = $(serviceName).val();
		var rt = $.ajax({
			url : "/UserManage/getResource",
			data : {
				serviceName : serviceName
			},
			async : false,
			dataType : 'json'
		}).responseText;
		rt = eval('(' + rt + ')');
		var obj = $(resourceId);
		obj.parent().children().remove("div");
		obj.removeClass();
		if (rt[0] == true) {
			for (var key in rt[1]) {
				var name = new Option(rt[1][key], rt[1][key]);
				//	var name = new Option(rt[1][key][1] + "(" + rt[1][key][2]+","+rt[1][key][3]+","+rt[1][key][4]+","+rt[1][key][5]+")", rt[1][key][1] + "(" + rt[1][key][2]+","+rt[1][key][3]+","+rt[1][key][4]+","+rt[1][key][5]+")");
				$(resourceId)[0].options.add(name);
			}
		}
		obj.addClass("chzn-select");
		$(".chzn-select").chosen();
	}

	function getAllTenementLevel(tenement, serviceType) {
		var serviceName = $(serviceType).val();
		var rt = $.ajax({
			url : "/UserManage/getAllTenementLevel",
			data : {
				serviceName : serviceName
			},
			async : false,
			dataType : 'json'
		}).responseText;
		rt = eval('(' + rt + ')');
		var obj = $(tenement);
		obj.parent().children().remove("div");
		obj.removeClass();
		if (rt[0] == true) {
			for (var i = 0; i < rt[1].length; i++) {
				var name = new Option(rt[1][i][0] + "(" + rt[1][i][1] + ")", rt[1][i][0] + "(" + rt[1][i][1] + ")");
				$(tenement)[0].options.add(name);
			}
		}
		obj.addClass("chzn-select");
		$(".chzn-select").chosen();
	}

	function getAllTenementLevel1(serviceName, tenement) {
		var serviceName = $(serviceName).val();
		var total = document.getElementById(tenement);
		var rt = $.ajax({
			url : "/UserManage/getAllTenementLevel",
			data : {
				serviceName : serviceName
			},
			async : false,
			dataType : 'json'
		}).responseText;
		rt = eval('(' + rt + ')');
		var obj = $(tenement);
		obj.parent().children().remove("div");
		obj.removeClass();
		if (rt[0] == true) {
			for (var i = 0; i < rt[1].length; i++) {
				var name = new Option(rt[1][i][0] + "(" + rt[1][i][1] + ")", rt[1][i][0] + "(" + rt[1][i][1] + ")");
				totalP = document.createElement("span");
				totalP.appendChild(document.createTextNode(rt[1][i][0]));
				total.appendChild(totalP);
				total.appendChild(document.createElement("br"));
			}
		}
		obj.addClass("chzn-select");
		$(".chzn-select").chosen();
	}

	function getUserTenement(userName, serviceName, tenementId) {
		var userName = $(userName).val();
		var serviceName = $(serviceName).val();
		var rt = $.ajax({
			url : "/UserManage/queryUserTenementByUserName",
			data : {
				userName : userName,
				serviceName : serviceName
			},
			async : false,
			dataType : 'json'
		}).responseText;
		rt = eval('(' + rt + ')');
		if (rt.length > 0) {
			document.getElementById(tenementId).innerHTML = rt[0][1];
		}
	}

	function getUserTenementForUser(serviceName, tenementId) {
		var serviceName = $(serviceName).val();
		var rt = $.ajax({
			url : "/UserManage/queryUserTenementByUserName",
			data : {
				userName : username,
				serviceName : serviceName
			},
			async : false,
			dataType : 'json'
		}).responseText;
		rt = eval('(' + rt + ')');
		document.getElementById(tenementId).innerHTML = rt[0][1];
	}

	function getUserName(callback) {
		var names = [];
		allsites = allsites;
		$.get('/UserManage/getUserlist', {
		}, function(serverResponse) {
			if (serverResponse[0] == true) {
				var obj = $("#user");
				obj.parent().children().remove("div");
				obj.removeClass();
				if (serverResponse[1] == 'all') {
					$("#user")[0].innerHTML = "";
					var user = document.getElementById("user");
					user.options.add(new Option("", ""));
					for (var key in serverResponse[2]) {
						var group = document.createElement('optgroup');
						for (var key2 in serverResponse[2][key]) {
							group.label = key2;
							group.style.display = "list-item";
							user.appendChild(group);
							for (var i = 0; i < serverResponse[2][key][key2].length; i++) {
								user.options.add(new Option(serverResponse[2][key][key2][i], serverResponse[2][key][key2][i]));
							}
						}
					}
                                        
				} else {
					for (var i = 0; i < serverResponse[2].length; i++) {
						var name = new Option(serverResponse[2][i], serverResponse[2][i]);
						names.push(name);
					}
					callback(names);
				}
                                       if($("#user")[0].options.length>0){
                                            $("#user")[0].options[1].selected=true;  
                                            getServiceNameA($("#user")[0].options[1].value);
                                            getUserInfoA($("#user")[0].options[1].value);
                                       }
				obj.addClass("chzn-select");
				$(".chzn-select").chosen();
			}
		}, 'json');
	}

	function userload(names) {
		$("#user")[0].options.length = 1;
		for (var i = 0; i < names.length; i++) {
			$("#user")[0].options.add(names[i]);
		}
	}

	function getUserNameLogout(callback) {
		var names = [];
		allsites = allsites;
		$.get('/UserManage/getUserlist', {
		}, function(serverResponse) {
			if (serverResponse[0] == true) {
				var obj = $(user_logout);
				obj.parent().children().remove("div");
				obj.removeClass();
				if (serverResponse[1] == 'all') {
					$("#user_logout")[0].innerHTML = "";
					$("#user_logout")[0].options.add(new Option("用户名", "choseUser"));
					var user = document.getElementById("user_logout");
					for (var key in serverResponse[2]) {
						var group = document.createElement('optgroup');
						for (var key2 in serverResponse[2][key]) {
							group.label = key2;
							user.appendChild(group);
							for (var i = 0; i < serverResponse[2][key][key2].length; i++) {
								user.options.add(new Option(serverResponse[2][key][key2][i], serverResponse[2][key][key2][i]));
							}
						}
					}
				} else {
					for (var i = 0; i < serverResponse[2].length; i++) {
						var name = new Option(serverResponse[2][i], serverResponse[2][i]);
						names.push(name);
					}
					callback(names);
				}
				obj.addClass("chzn-select");
				$(".chzn-select").chosen();
			}
		}, 'json');
	}

	function userloadLogout(names) {
		for (var i = 0; i < names.length; i++) {
			$("#user_logout")[0].options.add(names[i]);
		}
	}

	function getUserInfoA(userName) {
		var rt = $.ajax({
			url : "/UserManage/queryUserInfoA",
			data : {
				userName : userName
			},
			async : false,
			dataType : 'json'
		}).responseText;
		rt = eval('(' + rt + ')');
		document.getElementById("admin-username").innerHTML = rt[0][0];
		document.getElementById("admin-mailbox").innerHTML = rt[0][2];
		if ((rt[0][3] == 'all') && rt[0][4] == "\u0001") {
			document.getElementById("admin-registersite").innerHTML = "全站点管理员";
		} else if ((rt[0][3] == 'all')) {
			document.getElementById("admin-registersite").innerHTML = "全站点用户";
		} else if (rt[0][4] == "\u0001") {
			document.getElementById("admin-registersite").innerHTML = rt[0][3] + "站点管理员";
		} else {
			document.getElementById("admin-registersite").innerHTML = rt[0][3] + "站点用户";
		}
	}

	function getServiceNameA(userName) {
		var rt = $.ajax({
			url : "/UserManage/queryServiceNameA",
			data : {
				userName : userName
			},
			async : false,
			dataType : 'json'
		}).responseText;
		rt = eval('(' + rt + ')');
		if (rt[0].length != 0) {
                  $("#adminServiceType")[0].options.length = 0;
			for (var i = 0; i < rt[0].length; i++) {
				if (i == 0) {
					$("#" + rt[0][0]).addClass("activeservice");
					$("#" + rt[0][0] + "_service").addClass("services");
				}
				var name = new Option(rt[0][i], rt[0][i]);
				$("#adminServiceType")[0].options.add(name);
			}
		}
               if($("#adminServiceType")[0].options.length>0){
                  $("#adminServiceType")[0].options[0].selected=true;
                  var userName = $("#user").val();
                   var value = $("#adminServiceType").val();
                        $('.activeservice').hide();
                        $('.services').hide();
                        document.getElementById(value).innerHTML = "";
                        document.getElementById(value + '_service').innerHTML = "";
                        $('#' + value).show(100);
                        $('#' + value + '_service').show(100);
                        $('.activeservice').removeClass();
                        $('.services').removeClass();
                        $('#' + value).addClass("activeservice");
                        $('#' + value + '_service').addClass("services");
                        var rt = $.ajax({
                                url : "/UserManage/queryResourceOfUserA",
                                data : {
                                        userName : userName,
                                        serviceName : value
                                },
                                async : false,
                                dataType : 'json'
                        }).responseText;
                        rt = eval('(' + rt + ')');
                        var titleDiv = document.createElement("h1");
                        titleDiv.appendChild(document.createTextNode('服务资源配额' + '(' + userName + ':' + value + ')'));
                        if (rt[0] == true) {
                                var containerDiv = document.createElement("p");
                                for (var key in rt[1]) {
                                        var contentDiv = document.createTextNode(key + ":" + rt[1][key]);
                                        containerDiv.appendChild(contentDiv);
                                        containerDiv.appendChild(document.createElement('br'));
                                        containerDiv.appendChild(document.createElement('br'));
                                }
                                document.getElementById(value).appendChild(titleDiv);
                                document.getElementById(value).appendChild(document.createElement('br'));
                                document.getElementById(value).appendChild(containerDiv);
                        }

                        var rt = $.ajax({
                                url : "/UserManage/queryApiOfUserA",
                                data : {
                                        userName : userName,
                                        serviceName : value
                                },
                        async : false,
                                dataType : 'json'
                        }).responseText;
                        rt = eval('(' + rt + ')');
                        if (rt[0] == true) {
                                var titleDiv = document.createElement("ul");
                                for (var key in rt[1]) {
                                        var containerDiv = document.createElement("li");
                                        var containerDivChild = document.createElement("a");
                                        containerDivChild.href = "#";
                                        var contentDiv = document.createTextNode(key + ":" + rt[1][key]);
                                        containerDivChild.appendChild(contentDiv);
                                        containerDiv.appendChild(containerDivChild);
                                        titleDiv.appendChild(containerDiv);
                                }
                                document.getElementById(value + '_service').appendChild(document.createElement('br'));
                                document.getElementById(value + '_service').appendChild(titleDiv);
                        } 
               }
	}

	function getUserInfo() {
		var rt = $.ajax({
			url : "/UserManage/queryUserInfo",
			data : {
			},
			async : false,
			dataType : 'json'
		}).responseText;
		rt = eval('(' + rt + ')');
		username = rt[0][0];
		document.getElementById("userName").innerHTML = rt[0][0];
		document.getElementById("mailbox").innerHTML = rt[0][2];
		if (rt[0][3] == 'all') {
			document.getElementById("registersite").innerHTML = "全站点用户";
		} else {
			document.getElementById("registersite").innerHTML = rt[0][3]+"站点用户";
		}
	}

	function getServiceName() {
		var rt = $.ajax({
			url : "/UserManage/queryServiceName",
			data : {
			},
			async : false,
			dataType : 'json'
		}).responseText;
		rt = eval('(' + rt + ')');
		var obj = $("#serviceType");
		obj.parent().children().remove("div");
		obj.removeClass();
		if (rt[0].length != 0) {
			for (var i = 0; i < rt[0].length; i++) {
				if (i == 0) {
					$("#" + rt[0][0]).addClass("activeservice");
					$("#" + rt[0][0] + "_service").addClass("services");
				}
				var name = new Option(rt[0][i], rt[0][i]);
				$("#serviceType")[0].options.add(name);
			}
                                $("#serviceType")[0].options[0].selected=true;
		}
		obj.addClass("chzn-select");
		$(".chzn-select").chosen();
                var value = $("#serviceType").val();
                $('.activeservice').hide();
                $('.services').hide();
                $('#' + value).show(100);
                document.getElementById(value).innerHTML = "";
                document.getElementById(value + '_service').innerHTML = "";
                $('#' + value + '_service').show(100);
                $('.activeservice').removeClass();
                $('.services').removeClass();
                $('#' + value).addClass("activeservice");
                $('#' + value + '_service').addClass("services");
                $.post('/UserManage/queryResourceOfUser', {
                        serviceName : value
                }, function(serverResponse) {
                        result = serverResponse;
                        var titleDiv = document.createElement("h1");
                        titleDiv.appendChild(document.createTextNode('服务资源配额' + '(' + value + ')'));
                        if (result && result[0] == true) {
                                var containerDiv = document.createElement("p");
                                for (var key in result[1]) {
                                        var contentDiv = document.createTextNode(key + ":" + result[1][key]);
                                        containerDiv.appendChild(contentDiv);
                                        containerDiv.appendChild(document.createElement('br'));
                                        containerDiv.appendChild(document.createElement('br'));
                                }
                                document.getElementById(value).appendChild(titleDiv);
                                document.getElementById(value).appendChild(document.createElement('br'));
                                document.getElementById(value).appendChild(containerDiv);
                        }
                }, 'json');
                var rt = $.ajax({
                        url : "/UserManage/queryApiOfUser",
                        data : {
                                serviceName : value
                        },
                        async : false,
                        dataType : 'json'
                }).responseText;
                rt = eval('(' + rt + ')');
                if (rt[0] == true) {
                        var titleDiv = document.createElement("ul");
                        for (var key in rt[1]) {
                                var containerDiv = document.createElement("li");
                                var containerDivChild = document.createElement("a");
                                containerDivChild.href = "#";
                                var contentDiv = document.createTextNode(key + ":" + rt[1][key]);
                                containerDivChild.appendChild(contentDiv);
                                containerDiv.appendChild(containerDivChild);
                                titleDiv.appendChild(containerDiv);
                        }
                        document.getElementById(value + '_service').appendChild(titleDiv);
                }
	}

	var tableInitParams = {
		"sScrollX" : "100%",
		"sScrollXInner" : "100%",
		"bScrollCollapse" : true,
		"bJQueryUI" : true,
		"sPaginationType" : "full_numbers",
		"oLanguage" : {
			"sLengthMenu" : "  每页显示 _MENU_ ",
			"sZeroRecords" : "没有记录",
			"sInfo" : "显示 _START_ 到 _END_ 项记录，总共 _TOTAL_  项",
			"sInfoEmpty" : "没有记录",
			"sInfoFiltered" : "(从总共 _MAX_ 项记录中查找)"
		},
		"sDom" : '<"H"Tfr>t<"F"ip>',
		"iDisplayLength" : 10,
		"oTableTools" : {
			"sRowSelect" : "single",
			"aButtons" : []
		}
	};

	function initDataTable(domID, initParams, hasMultipleSelectionSupport) {
		var jquerySelector = '#' + domID;
		var table = $(jquerySelector).dataTable(initParams);
		if (hasMultipleSelectionSupport) {

		} else {
			$(jquerySelector + ' tbody').click(function(event) {
				$(table.fnSettings().aoData).each(function() {
					$(this.nTr).removeClass('row_selected');
				});
				$(event.target.parentNode).addClass('row_selected');
				var oTT = TableTools.fnGetInstance(domID);
				var anSelected = oTT.fnGetSelected();

				var a = $('td', anSelected);
				var tid = $(a[0]).text();
			});
		}
		return table;
	} ;

	userHpcTemplateInfoTable = initDataTable('userHpcTemplateInfoTable', tableInitParams, false);
	userHpcJobResultTable = initDataTable('userHpcJobResultTable', tableInitParams, false);
	adminHpcJobInfoTable = initDataTable('adminHpcJobInfoTable', tableInitParams, false);
	userHpcVirtualClusterTable = initDataTable('userHpcVirtualClusterTable', tableInitParams, false);
	adminHpcVirtualClusterInfoTable = initDataTable('adminHpcVirtualClusterInfoTable', tableInitParams, false);
	userHpcVirtualClusterTemplateTable = initDataTable('userHpcVirtualClusterTemplateTable', tableInitParams, false);
	userVMCreationTable = initDataTable('userVMCreationTable', tableInitParams, false);
	userCBSCreationTable = initDataTable('userCBSCreationTable', tableInitParams, true);
	userCBSAttachTable = initDataTable('userCBSAttachTable', tableInitParams, true);
	userImgTable = initDataTable('userImgTable', tableInitParams, false);
	adminIaaSVirtualMachineTable = initDataTable('adminIaaSVirtualMachineTable', tableInitParams, true);
	adminIaaSHostMachineTable = initDataTable('adminIaaSHostMachineTable', tableInitParams, false);
	userWebHostingInfoTable = initDataTable('userWebHostingInfoTable', tableInitParams, false);
	adminWebHostingServiceTable = initDataTable('adminWebHostingServiceTable', tableInitParams, false);
	adminWebHostingVMTable = initDataTable('adminWebHostingVMTable', tableInitParams, false);
	userSystemStatusVMTable = initDataTable('userSystemStatusVMTable', tableInitParams, false);
	adminSystemStatusHostTable = initDataTable('adminSystemStatusHostTable', tableInitParams, false);
	adminSystemStatusVMTable = initDataTable('adminSystemStatusVMTable', tableInitParams, false);
	adminUserManagementUserInfoTable = initDataTable('adminUserManagementUserInfoTable', tableInitParams, false);
	userHadoopClusterTable = initDataTable('userHadoopClusterTable', tableInitParams, false);
	userHadoopImageTable = initDataTable('userHadoopImageTable', tableInitParams, false);
	userVirtAppTable = initDataTable('userVirtAppTable', tableInitParams, false);
	adminComputingResourceTable = initDataTable('adminComputingResourceTable', tableInitParams, false);
	userVPCCreationTable = initDataTable('userVPCCreationTable', tableInitParams, false);
	userPrivateCloud = initDataTable('userPrivateCloud', tableInitParams, false);
	//adminGeneralTracesTable = initDataTable('adminGeneralTracesTable', tableInitParams, false);   
	//adminDetailsTracesTable = initDataTable('adminDetailsTracesTable', tableInitParams, false);   

});
