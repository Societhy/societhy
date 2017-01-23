app.controller('WalletController', function($rootScope, $http, $sessionStorage, $state) {

	var ctrl = this;

	init = function() {
		ctrl.user = $rootScope.user
	}

	ctrl.refreshAllBalances = function() {
		if (ctrl.user == undefined) {
			init();
		}
		$http.get('/getAllBalances').then(function(response) {
			$.each($rootScope.user.eth.keys, function(index, keyObject) {
				keyObject.balance = response.data[keyObject.address];
			});
			$rootScope.user.totalBalance = ctrl.totalBalance();
		});
	}

	ctrl.totalBalance = function() {
		var totalBalance = 0;
		$.each(ctrl.user.eth.keys, function(index, keyObject) {
			totalBalance += keyObject.balance;
		});
		return totalBalance;
	}

	ctrl.refreshBalance = function(address) {
		$http.get('/getBalance/'.concat(address)).then(function(response) {
			$rootScope.user.totalBalance = ctrl.totalBalance();
			$.each($rootScope.user.eth.keys, function(index, keyObject) {
				keyObject.balance = response.data[keyObject.address];
			});
		});
	};

	return ctrl;
});