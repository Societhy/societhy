app.controller('OrgaMainController', function($rootScope, $http, $sessionStorage, $state) {

	var ctrl = this;

	ctrl.init = function() {
		console.log($state.params);
		$http.post('/getOrganization', {
			"id": $state.params.orga_id
		}).then(
		function(data) {
			$rootScope.currentOrga = data;
			console.log(data);
		},
		function(error) {
			$rootScope.currentOrga = {"name": "one", "id": 1, "picture": "static/assets/images/orga_default.jpg"};
			console.log(error);
		});

	}

	ctrl.init()
	return ctrl;
});