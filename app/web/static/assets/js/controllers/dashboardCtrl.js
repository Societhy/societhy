'use strict';
/**
 * controllers used for the dashboard
 */
app.controller('DashboardCtrl',  function($scope, $rootScope, $http, $sessionStorage, $state, $controller, $location, socketIO) {
    var ctrl = this;
    $scope.values = [];



    ctrl.click_notif = function (notif)
    {
        console.log(notif);
        $state.go(notif.angularState.route, notif.angularState.params);
        $state.go(notif["angularState"]["route"], notif["angularState"]["params"]);
        $http.post("/markNotificationsAsRead", {"data" : [notif]}).then(function (response) {
            if (response.status = 200) {
                ctrl.updateNotif();
            }
        })

    };

    this.updateHome = function ()
    {
        $http.get("/getUserHomePage").then(function (response) {
            $scope.values = response.data.sort(function (a , b ) {
                return a.createdAt + b.createdAt;
            });
            console.log($scope.values);

        });
    };

    if ($rootScope.user)
    {
        this.updateHome();
        ctrl.user = $rootScope.user;
    }
    console.log("zigounette");
});
