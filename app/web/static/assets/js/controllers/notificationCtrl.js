/**
 * Controller for notification
 */
app.controller('NotificationController', function($scope, $rootScope, $http, $sessionStorage, $state, $controller, $location, socketIO) {
    var ctrl = this;
    ctrl.user = $rootScope.user;

    ctrl.click_notif = function (notif)
    {
        console.log(notif);
        $state.go(notif.angularState.route, notif.angularState.params);
        $state.go(notif["angularState"]["route"], notif["angularState"]["params"]);
    };

    socketIO.on('update_notif', function (data) {
       console.log(data)
    })
    return ctrl;
});