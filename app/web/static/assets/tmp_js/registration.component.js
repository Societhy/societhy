
angular.module('registration', [
	"ngCookies"]);

angular.module('registration').
controller('RegistrationController', function ($http, $cookies) {
	var ctrl = this;

	ctrl.name = null;
	ctrl.age = null;
	ctrl.email = null;
	ctrl.password = null;

	this.register = function() {
		if (ctrl.name && ctrl.password) {
			$http.post('/newUser', {
				name: ctrl.name,
				age: ctrl.age || "",
				email: ctrl.email || "",
				password: ctrl.password
			}).then(function(response) {
				console.log("RECEIVED = ", response);
				$cookies.put('token', response.data.token);
				ctrl.auth = "OUI !!!"
			});
		}
	};
});


angular.module('registration').
component('registration', {
	templateUrl: 'static/templates/registration.html',
	controller: 'RegistrationController',
	bindings: {
		auth: '='
	}
});
