app.controller('LoginController', function($rootScope, $http, $sessionStorage) {

//	var keythereum = require("keythereum");
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
				ctrl.password = CryptoJS.MD5(ctrl.password).toString();
				$http.post('/login', {
					"id": btoa(ctrl.username + ':' + ctrl.password)
				}).then(function(response) {
					console.log("RECEIVED = ", response);
					$sessionStorage.SociethyToken = response.data.token;
					$sessionStorage.username = response.data.user.name.replace(/\"/g, "");
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

    ctrl.test = $sessionStorage.username;

    ctrl.register = function() {
		if (ctrl.username && ctrl.password) {
			ctrl.password = CryptoJS.MD5(ctrl.password).toString();
		    $http.post('/newUser', {
				name: ctrl.username, email: ctrl.email,
				firstname: ctrl.firstname || "",
				lastname: ctrl.lastname || "",
				birthday: ctrl.birthday || "",
				gender: ctrl.gender || "",
				address: ctrl.address || "",
				city: ctrl.city || "",
				password: ctrl.password
			}).then(function(response) {
				console.log("RECEIVED = ", response);
				$sessionStorage.SociethyToken = response.data.token;
				$rootScope.user = response.data.user;
				},
				function(error) {
					console.log(error);
			});
		}
    };
	return ctrl
});
