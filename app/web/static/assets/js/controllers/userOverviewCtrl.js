app.controller('userOverviewCtrl', function($scope, $http, $timeout, $rootScope) {
 	var ctrl = this;

//OAuth

console.log("Initializing OAuth ..")
OAuth.initialize('xitTtb8VF8kr2NKmBhhKV_yKi4U');

ctrl.coinbase_connect = function ()
{
    OAuth.popup('coinbase').done(function(result) {
        console.log(result)
        result.me().done(function (data) {
            console.log(data);
        })
    })
}

ctrl.fb_connect = function () 
{
    res = OAuth.popup('facebook').done(function(facebook) {
        loginObject = facebook;
        facebook.get("/me").done(function(userData) {

            console.log(userData);

            $http.post('/updateUser', userData).then(function(response) {
                console.log("RECEIVED = ", response);
            }, function(error) {
                console.log(error);
            });
        });
    }).fail(function(err) {
        console.log(error);
    });
}

    $rootScope.updateUser = function(name) {
	if ($rootScope.user != null)
	{
	    $http.post('/updateSingleUserField', {
		"_id": $rootScope.user["_id"],
		"new": $rootScope.user[$rootScope.name],
		"old": $rootScope.oldVal,
		"name": $rootScope.name,
	    }).then(function(response) {
		$rootScope.user = ctrl.user = response.data;
	    },
		    function(error) {
			console.log(error);
		    });
	}
	else
	    console.log("User not logged in");
    }

    $rootScope.$watchGroup(['user.firstname'], function(newVal, oldVal) {
	console.log(42);
    });
    function animation() {
	$("input.userDataEditable").hover(function(){
	    $(this).css("border", "solid 2px rgba(66, 139, 202, 1)");
	}, function(){
     	    $(this).css("border", "solid 1px rgba(204, 204, 204, 1)");
	});
    };

    animation();

// //Load facebook SDK
// window.fbAsyncInit = function() {
// 	FB.init({
// 		appId      : '1774766892791379',
// 		xfbml      : true,
// 		version    : 'v2.8'
// 	});
// 	FB.AppEvents.logPageView();
// };

// (function(d, s, id){
// 	var js, fjs = d.getElementsByTagName(s)[0];
// 	if (d.getElementById(id)) {return;}
// 	js = d.createElement(s); js.id = id;
// 	js.src = "//connect.facebook.net/en_US/sdk.js";
// 	fjs.parentNode.insertBefore(js, fjs);
// }(document, 'script', 'facebook-jssdk'));

// ctrl.fb_connect = function (argument) {
// 	FB.login(function(response) {

// 		if (response.authResponse)
// 		{
//             access_token = response.authResponse.accessToken; //get access token
//             user_id = response.authResponse.userID; //get FB UID
//             console.log("token : " + access_token);
//             console.log("user_id : " + user_id);
//             FB.api('/me', {fields: 'email, name, picture'} ,function(response)
//             {
//                 console.log("name : " + response.name);
//                 console.log("email : " + response.email);
//                 console.log("photo url " + response.picture.data.url);

//                 newPhoto = angular.element(document.querySelector('#newPhoto'));
//                 newPhoto.html('<img src="'+ response.picture.data.url + '">')

//             });

//         } else {
//             //user hit cancel button
//             console.log('User cancelled login or did not fully authorize.');

//         }
//     }, {
//     	scope: 'public_profile,email'
//     });
    //}

});
