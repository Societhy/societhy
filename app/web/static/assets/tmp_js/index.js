app = angular.module("societhy", [
	"ngCookies",
	"user",
	]).config(function($httpProvider) {
		$httpProvider.interceptors.push('httpRequestInterceptor');
	});

app.controller('IndexController', function($scope, $http, $cookies) {
	var ctrl = this

	$scope.auth = "NON";
	$scope.user = null;
	$scope.login = function() {
		if ($scope.user && $scope.user.username && $scope.user.password) {
				$http.post('/login', {"id": btoa($scope.user.username + ':' + $scope.user.password)}).then(function(response) {
					if (response.status == 200) {
						console.log("RECEIVED = ", response);
						$cookies.put('token', response.data.token);
						$scope.auth = "OUI"
				}
			});
		}
	}

	$scope.logout = function() {
		$http.get('/logout').then(function(reponse) {
			console.log("RECEIVED = ", reponse);
			$scope.auth = "NON";
		});
	}
});

app.factory('httpRequestInterceptor', function($cookies) {
  return {
  	'request': function(config) {
  		if ($cookies.get('token')) {
  			config.headers.Authentification = $cookies.get('token');
  		}
  		console.log("SENDING", config)
  		return config;
  	}
  }
});
 