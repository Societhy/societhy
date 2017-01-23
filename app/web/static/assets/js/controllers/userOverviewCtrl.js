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
            $http.post('/updateUser', {"social" : 
                { "coinbase" : 
                {
                "firstname" : data.firstname,
                "lastname" : data.lastname,
                "email" : data.email,
                "id" : data.id,
                "company" : data.company,
            }}}
            ).then(function(response) {}, function(error) {
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
                {"social" : 
                {"facebook" :
                {
                    "firstname" : userData.first_name,
                    "lastname" : userData.last_name,
                    "id" : userData.id,
                    "email" : userData.email,
                    "pictureURL" : userData.picture.data.url
                }}}
                ).then(function(response) {
                    console.log(response);
                }, function(error) {
                    console.log(error);
                });
            });
    }).fail(function(err) {
        console.log(err);
    });
}

ctrl.twitter_connect = function ()
{
    OAuth.popup('twitter').done(function(result) {
        result.me().done(function(userData) {
            $http.post('/updateUser',
                {"social" : 
                {"twitter" :
                {
                    "firstname" : userData.name,
                    "id" : userData.id,
                    "email" : userData.email,
                    "pictureURL" : userData.avatar,
                    "url" : userData.url,
                }}}
                ).then(function(response) {
                    console.log(response);
                }, function(error) {
                    console.log(error);
                });
})
})
}

ctrl.linkedin_connect = function()
{
OAuth.popup('linkedin').done(function(result) {
    console.log(result)
    result.me().done(function(userData) {
            $http.post('/updateUser',
                {"social" : 
                {"linkedin" :
                {
                    "firstname" : userData.firstname,
                    "lastname" : userData.lastname,
                    "id" : userData.id,
                    "pictureURL" : userData.avatar,
                    "url" : userData.url,
                }}}
                ).then(function(response) {
                    console.log(response);
                }, function(error) {
                    console.log(error);
                });
    })
})
}

ctrl.github_connect = function ()
{
OAuth.popup('github').done(function(result) {
    console.log(result)
    result.me().done(function(userData) {
            $http.post('/updateUser',
                {"social" : 
                {"github" :
                {
                    "firstname" : userData.name,
                    "id" : userData.id,
                    "email" : userData.email,
                    "pictureURL" : userData.avatar,
                    "company" : userData.company,
                    "alias" : userData.alias
                }}}
                ).then(function(response) {
                    console.log(response);
                }, function(error) {
                    console.log(error);
                });
})
})
}

ctrl.google_connect = function ()
{
    console.log("hello");
    res = OAuth.popup('google').done(function(result)
    {
        result.me().done(function(userData) {
            console.log(userData);
            $http.post('/updateUser',
                {"social" : 
                {"google" :
                {
                    "firstname" : userData.firstname,
                    "lastname" : userData.lastname,
                    "id" : userData.id,
                    "email" : userData.email,
                    "pictureURL" : userData.avatar,
                    "url" : userData.url,
                    "company" : userData.company

                }}}
                ).then(function(response) {
                    console.log(response);
                }, function(error) {
                    console.log(error);
                });
            })
    }).then(function() {}, function(error) {
        console.log(error);
    });
}

$rootScope.updateUser = function(name, oldVal) {
	if ($rootScope.user != null)
	{
            $http.post('/updateSingleUserField', {
		"_id": $rootScope.user["_id"],
		"new": $rootScope.user[name],
		"old": oldVal,
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
    var fields = ['firstname', 'lastname', 'email','phone', 'address', 'city', 'birthday']
    $rootScope.$watch("user", function(newVal, oldVal, obj) {
	if ($rootScope.user != null && oldVal !== null && newVal !== oldVal) {
            for (var key in fields) {
		if ($rootScope.user[fields[key]] != oldVal[fields[key]]) {
		    $rootScope.updateUser(fields[key], oldVal[fields[key]])
		    return;
		}
            }
	}
    }, true);

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
    return ctrl;
});
