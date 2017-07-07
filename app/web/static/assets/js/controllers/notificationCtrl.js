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
    $http.post("/markNotificationsAsRead", {"data" : [notif]}).then(function (response) {
      if (response.status = 200) {
        ctrl.updateNotif();
      }
    })

  };

  ctrl.updateNotif = function ()
  {
    $http.get("/getUserUnreadNotification").then(function (response) {
      console.log("UNREAD NOTIFICATIONS : ", response.data);
      $rootScope.unread_notification = JSON.parse(response.data);
    });
  };

  ctrl.mark_all_as_read = function ()
  {
    $http.post("/markNotificationsAsRead", {"data" : $scope.unread_notification}).then(function (response) {
      console.log(response);
      if (response.status = 200)
      {
        ctrl.updateNotif();
      }
    })  
  };

  socketIO.on('update_notif', function (data) {
    ctrl.updateNotif();
    if ($rootScope.unread_notification.length != 0)
    {
      $rootScope.unread_notification.sort(function (a, b) {
        return a["date"] - b["date"]
      });
      last_one = $rootScope.unread_notification[$rootScope.unread_notification.length - 1];
      $rootScope.toogleInfo(last_one["description"]);
    }
  });

  if ($rootScope.user)
  {
    this.updateNotif();

  }

  return ctrl;
});
