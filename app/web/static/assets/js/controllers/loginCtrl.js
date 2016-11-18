app.controller('LoginController', function($rootScope, $http, $sessionStorage, $state) {

//	var keythereum = require("keythereum");
	var ctrl = this;

	if ($sessionStorage.SociethyToken != null && $rootScope.user == null) {
		$http.get('/checkTokenValidity/'.concat($sessionStorage.SociethyToken)).then(function(response) {
			if (response.data.user != null) {
				$rootScope.user = ctrl.user = response.data.user;
				console.log(ctrl.user)
			}
		});
	}
	else if ($rootScope.user != null) {
		ctrl.user = $rootScope.user
	}

	ctrl.login = function() {
		if (ctrl.username && ctrl.password) {
				$http.post('/login', {
					"id": btoa(ctrl.username + ':' + ctrl.password)
				}).then(function(response) {
					console.log("RECEIVED = ", response);
					$sessionStorage.SociethyToken = response.data.token;
					$sessionStorage.username = response.data.user.name.replace(/\"/g, "");
					$rootScope.user = ctrl.user = response.data.user;
				}, function(error) {
					console.log(error);
				});
		}
	}

	ctrl.logout = function() {
		$http.get('/logout').then(function(reponse) {
			delete $sessionStorage.SociethyToken;
			$rootScope.user = ctrl.user = null
			$state.go('app.dashboard');
		});
	}

    ctrl.register = function() {

		if (ctrl.username && ctrl.password) {
		    $http.post('/newUser', {
				name: ctrl.username,
				email: ctrl.email,
				password: ctrl.password,
				eth: ctrl.wantsKey || false,
				firstname: ctrl.firstname || "",
				lastname: ctrl.lastname || "",
				birthday: ctrl.birthday || "",
				gender: ctrl.gender || "",
				address: ctrl.address || "",
				city: ctrl.city || ""
			}).then(function(response) {
				console.log("RECEIVED = ", response);
				$sessionStorage.SociethyToken = response.data.token;
				$rootScope.user = ctrl.user = response.data.user;
				$state.go("app.me", ctrl)
				},
				function(error) {
					console.log(error);
			});
		}
    };
	return ctrl
});
