app.controller('userPreferenceCtrl', function($scope, $http, $timeout, $rootScope, $state, $controller, $sessionStorage) {
    var ctrl = this;

    if ($rootScope.user !== null)
    {
        this.notification_preference = $rootScope.user.notification_preference;
    }

    this.update = function ()
    {
        $http.post('/updateUser',
            {
                "notification_preference" : this.notification_preference
            }
        ).then(function(response) {
            $rootScope.user = response.data;
            ctrl.notification_preference = $rootScope.user.notification_preference;
        }, function(error)
        {
            console.log(error);
        });
    }
});