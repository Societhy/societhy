'use strict';
/**
 * controller for Messages
 */

app.controller('ChatCtrl', function ($scope, $rootScope, socketIO) {
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

        socketIO.emit('join', {'name': $scope.user.name,
        'id': $scope.selfIdUser,
        'otherId': $scope.otherIdUser});
    }

    $scope.addUser = function (user) {
        $scope.usersList.push(user);
    }

    var receiveMessage = function (data) {
        var newMessage = {
            "avatar": data.avatar,
            "date": data.date,
            "content": data.content,
            "idUser": data.idUser,
            "idOther": data.idOther
        };
        $scope.chat.push(newMessage);
        $scope.chatMessage = '';
    };

    socketIO.on('send_message', function (data) {
        receiveMessage(data);
    })

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
            socketIO.emit('send_message', newMessage);
        }
        $scope.chatMessage = '';
    };
});
