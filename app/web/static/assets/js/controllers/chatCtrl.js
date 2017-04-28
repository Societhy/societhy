'use strict';
/**
 * Controller for chat.
 *
 * @class ChatCtrl
 */

 app.controller('ChatCtrl', function ($scope, $rootScope, $http, socketIO) {
    $scope.user = $rootScope.user;

    /**
     * Load all necessary ressources and initialize the connection with the chat server.
     *
     * @method load
     */
    var load = function () {
        $scope.user = $rootScope.user;
        $scope.noAvatarImg = "static/assets/images/default-user.png";
        $scope.usersList = [];
        $scope.otherIdUser = "";
        $scope.otherName = "";
        $scope.chat = [];
        if ($scope.user) {
            $scope.usersList = $scope.user.contact_list;
            $scope.selfIdUser = $scope.user._id;
            socketIO.emit('init', {"id": $scope.selfIdUser});
            console.log('chat ctrl loaded')
        }
    }

    /**
     * Set the conversation window to the user selected.
     * @param {string} id - The id of the user selected.
     * @param {string} firstname - The firstname of the user.
     * @param {string} lastname - The lastname of the user.
     *
     * @method setChat
     */
    $scope.setChat = function (id, firstname, lastname) {
        $scope.otherIdUser = id;
        $scope.otherName = firstname + " " + lastname;
        $scope.chat = [];

        socketIO.emit('join', {'name': $scope.user.name,
            'id': $scope.selfIdUser,
            'otherId': $scope.otherIdUser});
    }

    /**
     * Add a user to the contact list.
     * @param {json} user
     * @deprecated not used anymore.
     * @method addUser
     */
    $scope.addUser = function (user) {
        $scope.usersList.push(user);
    }

    /**
     * Add a new message to the list chat.
     * @param {message} data - The message data.
     * @method receiveMessage
     */
    var receiveMessage = function (data) {
        var newMessage = {
            "date": data.date,
            "content": data.data,
            "idUser": data.send_address,
            "idOther": data.recip_address,
            "avatar": data.avatar
        };
        $scope.chat.push(newMessage);
        $scope.chatMessage = '';
    };

    /**
     * SocketIo event triggered when a new message income.
     * @param {message} data - The message data.
     * @event send_message
     */
    socketIO.on('send_message', function (data) {
        receiveMessage(data);
    })

    /**
     * SocketIo event triggered when the server push the last messages of the conversation.
     * @param {list} data - The list of the last messages.
     * @event last_messages
     */
    socketIO.on('last_messages', function (data) {
        data = JSON.parse(data);
        for (var message in data) {
            receiveMessage(data[message]);
        }
    })

    /**
     * SocketIo event triggered when the server send the session ID. Used to synchronize user with is session ID.
     * @param {number} data - The session ID.
     * @event sessionId
     */
    socketIO.on('sessionId', function (data) {
        $rootScope.sessionId = data;
        if ($rootScope.user && data != $rootScope.user.socketid ) {
            $http.get('/socketid/'.concat($rootScope.sessionId)).then(function(resp) {
                $rootScope.user = resp.data
                console.log($rootScope.user)
            });
        }
    });

    // socketIO.on('txResult', function (data) {
    //     console.log("yesy", data);
    // })

    /**
     * SocketIo event triggered when a user not in the contact list send a message.
     * Change the contact list with the new one.
     * @param {list} data - The new contact list.
     * @event new_contact_list
     */
    socketIO.on('new_contact_list', function (data) {
        $rootScope.user.contact_list = data;
        $scope.user = $rootScope.user;
        $scope.usersList = $scope.user.contact_list;
    })

    /**
     * Send the current typed message and send it via SocketIo to the server.
     * @method sendMessage
     */
    $scope.sendMessage = function () {
        var newMessage = {
            "date": new Date(),
            "content": $scope.chatMessage,
            "idUser": $scope.selfIdUser,
            "idOther": $scope.otherIdUser,
            "avatar": $scope.noAvatarImg,
            "files": null
        };
        if (newMessage.content != '') {
            $scope.chat.push(newMessage);
            socketIO.emit('send_message', newMessage);
        }
        $scope.chatMessage = '';
    };

    /**
     * Angular event triggered when chat must be reloaded.
     * @event loadChat
     */
    $rootScope.$on('loadChat', function(event, data) {
        load();
    });

    /**
     * Angular event triggered when chat must be reloaded after login.
     * @event loggedIn
     */
    $rootScope.$on('loggedIn', function(event, data) {
        load();
    });

    load();
});
