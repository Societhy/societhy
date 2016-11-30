'use strict';
/**
 * controller for Messages
 */
app.controller('InboxCtrl', ["$scope", "$state", "$interval", "$rootScope",
function ($scope, $state, $interval, $rootScope) {
    $scope.user = $rootScope.user;

    $scope.noAvatarImg = "static/assets/images/default-user.png";
    var date = new Date();
    var d = date.getDate();
    var m = date.getMonth();
    var y = date.getFullYear();
    $scope.messages = [{
        "from": "John Stark",
        "date": new Date(y, m, d - 1, 19, 0),
        "subject": "Reference Request - Nicole Bell",
        "email": "stark@example.com",
        "avatar": null,
        "starred": false,
        "sent": false,
        "spam": false,
        "read": false,
        "content": "<p>Hi Peter, <br>Thanks for the e-mail. It is always nice to hear from people, especially from you, Scott.</p> <p>I have not got any reply, a positive or negative one, from Seibido yet.<br>Let's wait and hope that it will make a BOOK.</p> <p>Have you finished your paperwork for Kaken and writing academic articles?<br>If you have some free time in the near future, I want to meet you and explain to you our next project.</p> <p>Why not drink out in Hiroshima if we are accepted?<br>We need to celebrate ourselves, don't we?<br>Let's have a small end-of-the-year party!</p> <p>Sincerely, K. Nakagawa</p>",
        "id": 50223456
    }];


    var incomingMessages = [
		{
		    "from": "Nicole Bell",
		    "date": new Date(),
		    "subject": "New Project",
		    "email": "nicole@example.com",
		    "avatar": null,
		    "starred": false,
		    "sent": false,
		    "read": false,
		    "spam": false,
		    "content": "Hi there! Are you available around 2pm today? I’d like to talk to you about a new project",
		    "id": 50223466
		}
    ];


    $scope.scopeVariable = 1;
    var loadMessage = function () {
        $scope.messages.push(incomingMessages[$scope.scopeVariable - 1]);
        $scope.scopeVariable++;
    };

    //Put in interval, first trigger after 10 seconds
    var add = $interval(function () {
        if ($scope.scopeVariable < 2) {
            loadMessage();
        }
    }, 10000);

    $scope.stopAdd = function () {
        if (angular.isDefined(add)) {
            $interval.cancel(add);
            add = undefined;
        }
    };
}]);

app.controller('ViewMessageCrtl', ['$scope', '$stateParams',
function ($scope, $stateParams) {
    function getById(arr, id) {
        for (var d = 0, len = arr.length; d < len; d += 1) {
            if (arr[d].id == id) {

                return arr[d];
            }
        }
    }


    $scope.message = getById($scope.messages, $stateParams.inboxID);

}]);
