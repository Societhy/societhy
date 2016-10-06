
angular.module('user', ['registration']);

angular.module('user').
controller('ProfileController', function ($scope, $http) {
	var ctrl = this
	this.name = "?????";

	this.check_auth = function() {
		$http.get('/user/simon').then(function(data) {
			console.log("RECEIVING ", data)
			ctrl.auth = "OUI !!!"
		}, function(err) {
			ctrl.auth = "NON :((((("
		});
	}
});


angular.module('user').
component('profile', {
	templateUrl: 'static/templates/profile.html',
	controller: 'ProfileController',
	bindings: {
		auth: "="
	}
});
