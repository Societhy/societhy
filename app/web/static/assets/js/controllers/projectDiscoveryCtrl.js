app.controller('ProjectDiscoveryController', function($rootScope, $scope, $http, $sessionStorage, $state) {

	var ctrl = this;

	$http.get('/getAllProjects').then(function(resp) {
		console.log(resp);
		$scope.projects = resp.data;
	});
	return ctrl;
});
