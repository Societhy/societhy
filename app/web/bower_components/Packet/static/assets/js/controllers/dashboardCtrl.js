'use strict';
/**
 * controllers used for the dashboard
 */
app.controller('DashboardCtrl',  function($scope, $rootScope, $http, $sessionStorage, $state, $controller, $location, socketIO) {
    var ctrl = this;

    this.updateHome() = function ()
    {
        $http.get("/getUserHomePage").then(function (response) {
            console.log("HOMEPAGE : ", response.data);
            $rootScope.unread_notification = JSON.parse(response.data);
        });

    }

    if ($rootScope.user)
    {
        this.updateHome();
        ctrl.user = $rootScope.user;
    }
    console.log("zigounette");
}]);
