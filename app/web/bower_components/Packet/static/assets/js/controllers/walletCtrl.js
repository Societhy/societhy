app.controller('WalletController', function($rootScope, $http, $sessionStorage, $state) {

	$rootScope.wallet = this
	var ctrl = this;
	ctrl.user = $rootScope.user

	ctrl.refreshAllBalances = function() {
		$http.get('/getAllBalances').then(function(response) {
			console.log(response);
		});
	}

	ctrl.refreshAllBalances()
});