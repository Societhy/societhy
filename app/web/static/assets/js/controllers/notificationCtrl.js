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
    
    ctrl.mark_all_as_read = function ()
    {
      $http.post("/markNotificationsAsRead", $scope.unread_notification).then(function (response) {
          console.log(response);
      })  
    };

    socketIO.on('update_notif', function (data) {
        $http.get("/getUserUnreadNotification").then(function (response) {
            console.log(response);
            $rootScope.unread_notification = JSON.parse(response.data);
            $rootScope.unread_notification.sort(function(a, b)
            {
                return a["date"] - b["date"]
            });
            console.log("aaaaaaaaaaaa");
            last_one = $rootScope.unread_notification[$rootScope.unread_notification.length -1];
            $rootScope.toogleInfo(last_one["description"]);
        });
    });
    return ctrl;

});