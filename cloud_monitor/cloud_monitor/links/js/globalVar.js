var allsites;
var siteforiaas,siteforwebpaas,siteforhpc;
var username,adminuserName;
var responseforuser;

function getUserSites() {
	$.get('/ClusterNodes/getUserValidSite',
        function(serverResponse) {
			allsites=serverResponse;
		},
		'json');
}

getUserSites();
