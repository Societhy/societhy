app.controller('OrgaMainController', function($rootScope, $http, $sessionStorage, $state) {

	var ctrl = this;

	ctrl.init = function() {
		console.log($state.params);
		$http.post('/getOrganization', {
			"id": $state.params.orga_id
		}).then(
		function(data) {
			console.log(data);
		},
		function(error) {
			console.log(error);
		});

	}

	ctrl.init()
	return ctrl;
});