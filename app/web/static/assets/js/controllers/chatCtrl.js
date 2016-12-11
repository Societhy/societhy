'use strict';
/**
 * controller for Messages
 */
app.controller('ChatCtrl', ["$scope", "$rootScope", function ($scope, $rootScope, socket) {

    $scope.user = $rootScope.user;

    $scope.noAvatarImg = "static/assets/images/default-user.png";
    if ($scope.user) {
        $scope.selfIdUser = $scope.user._id;
    }
    $scope.otherIdUser = "";

    $scope.usersList = [{name:"Bob", job:"Barber", id:"idfromserver", avatar:$scope.noAvatarImg}];
    $scope.chat = [];

    $scope.setOtherId = function (id) {
        $scope.otherIdUser = id;
        console.log($scope.otherIdUser);
    }

    $scope.addUser = function (user) {
        $scope.usersList.push(user);
    }

    $scope.receiveMessage = function () {
        var newMessage = {
            "avatar": $scope.noAvatarImg,
            "date": new Date(),
            "content": $scope.chatMessage,
            "idUser": $scope.otherIdUser,
            "idOther": $scope.selfIdUser
        };
        $scope.chat.push(newMessage);
        $scope.chatMessage = '';
    };

    $scope.sendMessage = function () {
        var newMessage = {
            "avatar": "static/assets/images/avatar-1.jpg",
            "date": new Date(),
            "content": $scope.chatMessage,
            "idUser": $scope.selfIdUser,
            "idOther": $scope.otherIdUser
        };
        if (newMessage.content != '') {
            $scope.chat.push(newMessage);
        }
        console.log(socket);
        $scope.chatMessage = '';
    };
}]);
