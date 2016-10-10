'use strict';
/**
 * controller for Messages
 */
app.controller('ChatCtrl', ["$scope", function ($scope) {

    $scope.selfIdUser = 50223456;
    $scope.otherIdUser = 50223457;
    $scope.setOtherId = function (value) {

        $scope.otherIdUser = value;
    };
    var exampleDate = new Date().setTime(new Date().getTime() - 240000 * 60);

    $scope.chat = [{
        "user": "Simon Vadée",
        "avatar": "static/assets/images/avatar-1.jpg",
        "to": "Nicole Bell",
        "date": exampleDate,
        "content": "Hi, Nicole",
        "idUser": 50223456,
        "idOther": 50223457
    }];

    $scope.sendMessage = function () {
        var newMessage = {
            "user": "Simon Vadée",
            "avatar": "static/assets/images/avatar-1.jpg",
            "date": new Date(),
            "content": $scope.chatMessage,
            "idUser": $scope.selfIdUser,
            "idOther": $scope.otherIdUser
        };
        $scope.chat.push(newMessage);
        $scope.chatMessage = '';

    };
}]);
