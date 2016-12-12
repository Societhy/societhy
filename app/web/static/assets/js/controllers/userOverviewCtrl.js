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
            $http.post('/updateUser', { "coinbase" : {
                "firstname" : data.firstname,
                "lastname" : data.lastname,
                "email" : data.email,
                "id" : data.id,
                "company" : data.company, 
            }}).then(function(response) {}, function(error) {
                console.log(error);
            });
        })
    })
}

ctrl.fb_connect = function ()
{
    res = OAuth.popup('facebook').done(function(facebook) {
        loginObject = facebook;
        facebook.get("/me?fields=id,first_name,last_name,picture,email").done(function(userData) {
            console.log(userData);
            $http.post('/updateUser', 
                {"facebook" : 
                {
                    "firstname" : userData.first_name,
                    "lastname" : userData.last_name,
                    "id" : userData.id,
                    "email" : userData.email,
                    "pictureURL" : userData.picture.data.url
                }}
                ).then(function(response) {
                    console.log(response);
            }, function(error) {
                console.log(error);
            });
        });
    }).fail(function(err) {
        console.log(error);
    });
}

    /*
    ** Update one field from the user
    */
    $rootScope.updateUser = function(name, vals) {
	if ($rootScope.user != null)
	{
	    $http.post('/updateSingleUserField', {
		"_id": $rootScope.user["_id"],
		"new": vals[0],
		"old": vals[1],
		"name": name
	    }).then(function(response) {
		$rootScope.user = ctrl.user = response.data;
	    },
		    function(error) {
			$rootScope.user[name] = ctrl.user[name] = oldVal;
			console.log(error);
		    });
	}
	else
	    console.log("User not logged in");
    }

    /*
    ** Watch user data for any modifications
    */
    Array.prototype.diff = function(a) {
	return this.filter(function(i) {return a.indexOf(i) < 0;});
    };
    $rootScope.$watchGroup(['user.firstname', 'user.lastname', 'user.email','user.phone', 'user.address', 'user.city', 'user.birthday'], function(newVal, oldVal, obj) {
	vals = [
	    ((newVal.diff(oldVal).length != 0) ? newVal.diff(oldVal)[0] : ""),
	    ((oldVal.diff(newVal).length != 0) ? oldVal.diff(newVal)[0] : "")]
	if ($rootScope.user != null && newVal !== oldVal) {
	    for (var key in $rootScope.user) {
		if ($rootScope.user[key] == vals[0]) {
		    $rootScope.updateUser(key, vals)
		}
	    }
	}
    });


    /*
    ** Animate user info's inputs
    */
    function animation() {
	$("a.userDataEditable").hover(function() {
	    $(this).css("border", "solid 2px rgba(66, 139, 202, 1)");
	}, function() {
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

    return ctrl;
});
