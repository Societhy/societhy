app.controller('OrgaMainController', function($rootScope, $http, $sessionStorage, $state) {

	var ctrl = this;

	ctrl.init = function() {
		console.log($state.params);
		$http.post('/getOrganization', {
			// "name": $state.params.orga_id
			"name": $state.params.orga_name
		}).then(
		function(data) {
			$rootScope.currentOrga = data.data;
			console.log(data);
		},
		function(error) {
			$rootScope.currentOrga = {"name": "one", "id": 1, "picture": "static/assets/images/orga_default.jpg"};
			console.log(error);
		});
	}

	ctrl.joinOrga = function() {
		password = "test";
		if ($rootScope.user.local_account == true) {
			console.log("ask for password")
		}
		else {
			$http.post('/joinOrga', {
				"orga_id": $rootScope.currentOrga._id,
				"password": password
			}).then(
			function(data) {
				console.log(data);
			},
			function(error) {
				console.log(error);
			});
		}
	}

	ctrl.init()
	return ctrl;
});

