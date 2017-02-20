app.controller('OrgaDiscoveryController', function($rootScope, $scope, $http, $sessionStorage, $state) {

	var ctrl = this;

	console.log("get all orgas");
	$http.get('/getAllOrganizations').then(function(resp) {
		console.log(resp);
		$scope.organizations = resp.data;
	});
	return ctrl;
});

