app.controller('LoginController', function($rootScope, $http, $sessionStorage) {
	
	var ctrl = this;
	ctrl.coucou = "coucou";
	if ($sessionStorage.SociethyToken != null && $rootScope.user == null) {
		$http.get('/checkTokenValidity/'.concat($sessionStorage.SociethyToken)).then(function(response) {
			if (response.data.user != null) {
				$rootScope.user = response.data.user;
			}
		});
	}

	ctrl.login = function() {
		if (ctrl.username && ctrl.password) {
				$http.post('/login', {
					"id": btoa(ctrl.username + ':' + ctrl.password)
				}).then(function(response) {
					console.log("RECEIVED = ", response);
					$sessionStorage.SociethyToken = response.data.token;
					$rootScope.user = response.data.user;
				}, function(error) {
					console.log(error);
				});
		}
	}

	ctrl.logout = function() {
		$http.get('/logout').then(function(reponse) {
			delete $sessionStorage.SociethyToken;
			$rootScope.user = null;
		});
	}

	ctrl.register = function() {
		console.log("bite")
		if (ctrl.username && ctrl.password) {
			$http.post('/newUser', {
				name: ctrl.username,
				age: ctrl.age || "",
				email: ctrl.email || "",
				password: ctrl.password
			}).then(function(response) {
				console.log("RECEIVED = ", response);
				$cookies.put('token', response.data.token);
			}, function(error) {
					console.log(error);
			});
		}
	};
	return ctrl
});