app.controller('OrgaMainController', function($rootScope, $http, $sessionStorage, $state) {

	var ctrl = this;

	ctrl.init = function() {
		$http.get('/getOrganisation/'.concat($state.params.organization)).then(
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