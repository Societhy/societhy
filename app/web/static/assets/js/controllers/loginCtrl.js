/**
 * Controller for login.
 *
 * @class LoginCtrl
 */

 app.controller('LoginController', function($scope, ngNotify, $rootScope, $http, $sessionStorage, $state, $controller, $location) {

 	OAuth.initialize('xitTtb8VF8kr2NKmBhhKV_yKi4U');

 	var ctrl = this;
 	ctrl.user = $rootScope.user;
 	ctrl.wallet = $controller("WalletController");

 	if (ctrl.user) {
 		ctrl.wallet.refreshAllBalances();
 	}

    /**
     * Ask for login to the server.
     * @method login
     */

     ctrl.login_done = function () {
     	$http.get("/getUserUnreadNotification").then(function (response) {
     		$rootScope.unread_notification = JSON.parse(response.data);
     	});
     };

     ctrl.login = function() {
     	if (ctrl.username && ctrl.password) {
     		$http.post('/login', {
     			"id": btoa(ctrl.username + ':' + ctrl.password),
     			"socketid": $rootScope.sessionId
     		}).then(function(response) {
     			$sessionStorage.user = JSON.stringify(response.data.user);
     			$sessionStorage.SociethyToken = response.data.token;
     			$sessionStorage.username = response.data.user.name;
     			$rootScope.user = ctrl.user = response.data.user;
     			ctrl.wallet.refreshAllBalances();
     			console.log("USER IS SET in login : ", $rootScope.user);
     			$rootScope.$emit("loggedIn", '');
     			ctrl.login_done();
     		}, function(error) {
     			$rootScope.toogleError(error.data);
     		});
     	}
     };

    /**
     * Logout from the server.
     * @method logout
     */
     ctrl.logout = function() {
     	$http.get('/logout').then(function(reponse) {
     		delete $sessionStorage.SociethyToken;
     		$rootScope.user = ctrl.user = null
     		$state.go('app.dashboard');
     	});
     }


/**
 * Registration via coinbase.
 * @method coinbase_register
 */
 ctrl.coinbase_register = function ()
 {
 	OAuth.popup('coinbase').done(function(result) {
 		console.log(result)
 		result.me().done(function (data) {
 			$http.post('/newUser', {"social" :
 				{ "coinbase" :
 				{
 					"firstname" : data.firstname,
 					"lastname" : data.lastname,
 					"email" : data.email,
 					"id" : data.id,
 					"company" : data.company,
 				}
 			}
 		}).then(function(response) {
 			$sessionStorage.SociethyToken = response.data.token;
 			$rootScope.user = ctrl.user = response.data.user;
 			$rootScope.$emit("loggedIn", '');
 			$state.go("app.me", ctrl, {reload: true})
 		}, function(error) {
 			$rootScope.toogleError(error.data);
 			console.log(error);
 		});
 	})
 	})
 }

/**
 * Registration via facebook.
 * @method facebook_register
 */
 ctrl.fb_register = function ()
 {
 	res = OAuth.popup('facebook').done(function(facebook) {
 		loginObject = facebook;
 		facebook.get("/me?fields=id,first_name,last_name,picture,email").done(function(userData) {
 			$http.post('/newUser',
 				{"social" :
 				{"facebook" :
 				{
 					"firstname" : userData.first_name,
 					"lastname" : userData.last_name,
 					"id" : userData.id,
 					"email" : userData.email,
 					"pictureURL" : userData.picture.data.url
 				}
 			},
 			"socketid": $rootScope.sessionId
 		}).then(function(response) {
 			$sessionStorage.SociethyToken = response.data.token;
 			$rootScope.user = ctrl.user = response.data.user;
 			$rootScope.$emit("loggedIn", '');
 			console.log("USER IS SET in register : ", $rootScope.user);
 			$state.go("app.me", ctrl, {reload: true})
 		}, function(error) {
 			$rootScope.toogleError(error.data);
 			console.log(error);
 		});
 	});
 	}).fail(function(err) {
 		console.log(err);
 	});
 }

/**
 * Registration via twitter.
 * @method twitter_register
 */
 ctrl.twitter_register = function ()
 {
 	OAuth.popup('twitter').done(function(result) {
 		result.me().done(function(userData) {
 			$http.post('/newUser',
 				{"social" :
 				{"twitter" :
 				{
 					"firstname" : userData.name,
 					"id" : userData.id,
 					"email" : userData.email,
 					"pictureURL" : userData.avatar,
 					"url" : userData.url,
 				}
 			},
 			"socketid": $rootScope.sessionId
 		}).then(function(response) {
 			$sessionStorage.SociethyToken = response.data.token;
 			$rootScope.user = ctrl.user = response.data.user;
 			$rootScope.$emit("loggedIn", '');
 			console.log("USER IS SET in register : ", $rootScope.user);
 			$state.go("app.me", ctrl, {reload: true})
 			console.log(response);
 		}, function(error) {
 			$rootScope.toogleError(error.data);
 			console.log(error);
 		});
 	})
 	})
 }

/**
 * Registration via linkedin.
 * @method linkedin_register
 */
 ctrl.linkedin_register = function()
 {
 	OAuth.popup('linkedin').done(function(result) {
 		console.log(result)
 		result.me().done(function(userData) {
 			$http.post('/newUser',
 				{"social" :
 				{"linkedin" :
 				{
 					"firstname" : userData.firstname,
 					"lastname" : userData.lastname,
 					"id" : userData.id,
 					"pictureURL" : userData.avatar,
 					"url" : userData.url,
 				}},
 				"socketid": $rootScope.sessionId
 			}).then(function(response) {
 				$sessionStorage.SociethyToken = response.data.token;
 				$rootScope.user = ctrl.user = response.data.user;
 				$rootScope.$emit("loggedIn", '');
 				console.log("USER IS SET in register : ", $rootScope.user);
 				$state.go("app.me", ctrl, {reload: true})
 				console.log(response);
 			}, function(error) {
 				$rootScope.toogleError(error.data);
 				console.log(error);
 			});
 		})
 	})
 }

/**
 * Registration via github.
 * @method github_register
 */
 ctrl.github_register = function ()
 {
 	OAuth.popup('github').done(function(result) {
 		console.log(result)
 		result.me().done(function(userData) {
 			$http.post('/newUser',
 				{"social" :
 				{"github" :
 				{
 					"firstname" : userData.name,
 					"id" : userData.id,
 					"email" : userData.email,
 					"pictureURL" : userData.avatar,
 					"company" : userData.company,
 					"alias" : userData.alias
 				}},
 				"socketid": $rootScope.sessionId
 			}).then(function(response) {
 				console.log(response);
 				$sessionStorage.SociethyToken = response.data.token;
 				$rootScope.user = ctrl.user = response.data.user;
 				$rootScope.$emit("loggedIn", '');
 				console.log("USER IS SET in register : ", $rootScope.user);
 				$state.go("app.me", ctrl, {reload: true})

 			}, function(error) {
 				$rootScope.toogleError(error.data);
 				console.log(error);
 			});
 		})
 	})
 }

/**
 * Registration via google.
 * @method google_register
 */
 ctrl.google_register = function ()
 {
 	console.log("hello");
 	res = OAuth.popup('google').done(function(result)
 	{
 		result.me().done(function(userData) {
 			console.log(userData);
 			$http.post('/newUser',
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
 				}
 			},
 			"socketid": $rootScope.sessionId
 		}).then(function(response) {
 			$sessionStorage.SociethyToken = response.data.token;
 			$rootScope.user = ctrl.user = response.data.user;
 			$rootScope.$emit("loggedIn", '');
 			console.log("USER IS SET in register : ", $rootScope.user);
 			$state.go("app.me", ctrl, {reload: true})
 			console.log(response);
 		}, function(error) {
 			$rootScope.toogleError(error.data);
 			console.log(error);
 		});
 	})
 	}).then(function() {}, function(error) {
 		$rootScope.toogleError(error.data);
 		console.log(error);
 	});
 }


/**
 * Connection via coinbase.
 * @method coinbase_connect
 */
 ctrl.coinbase_connect = function ()
 {
 	OAuth.popup('coinbase').done(function(result) {
 		console.log(result)
 		result.me().done(function (data) {
 			$http.post('/login', {
 				"provider": "coinbase",
 				"socialId": data.id,
 				"socketid": $rootScope.sessionId
 			}).then(function(response) {
 				console.log("RECEIVED = ", response);
 				sessionStorage.user = JSON.stringify(response.data.user);
 				$sessionStorage.SociethyToken = response.data.token;
 				$sessionStorage.username = response.data.user.name;
 				$rootScope.user = ctrl.user = response.data.user;
 				console.log("USER IS SET in connect : ", $rootScope.user);
 				ctrl.wallet.refreshAllBalances();
 				$rootScope.$emit("loggedIn", '');
 				ctrl.login_done();
 			}, function(error) {
 				$rootScope.toogleError(error.data);
 				console.log(error);
 			});
 		})
 	})
 }

/**
 * Connection via facebook.
 * @method fb_connect
 */
 ctrl.fb_connect = function ()
 {
 	res = OAuth.popup('facebook').done(function(facebook) {
 		loginObject = facebook;
 		facebook.get("/me?fields=id,first_name,last_name,picture,email").done(function(userData) {
 			$http.post('/login', {
 				"provider": "facebook",
 				"socialId": userData.id,
 				"socketid": $rootScope.sessionId
 			}).then(function(response) {
 				console.log("RECEIVED = ", response);
 				sessionStorage.user = JSON.stringify(response.data.user);
 				$sessionStorage.SociethyToken = response.data.token;
 				$sessionStorage.username = response.data.user.name;
 				$rootScope.user = ctrl.user = response.data.user;
				console.log("USER IS SET in connect : ", $rootScope.user);
 				ctrl.wallet.refreshAllBalances();
 				$rootScope.$emit("loggedIn", '');
 				ctrl.login_done();
 			}, function(error) {
 				$rootScope.toogleError(error.data);
 				console.log(error);
 			});
 		});
 	}).fail(function(err) {
 		console.log(err);
 	});
 }

/**
 * Connection via twitter.
 * @method twitter_connect
 */
 ctrl.twitter_connect = function ()
 {
 	OAuth.popup('twitter').done(function(result) {
 		result.me().done(function(userData) {
 			$http.post('/login', {
 				"provider": "twitter",
 				"socialId": userData.id,
 				"socketid": $rootScope.sessionId
 			}).then(function(response) {
 				console.log("RECEIVED = ", response);
 				sessionStorage.user = JSON.stringify(response.data.user);
 				$sessionStorage.SociethyToken = response.data.token;
 				$sessionStorage.username = response.data.user.name;
 				$rootScope.user = ctrl.user = response.data.user;
				console.log("USER IS SET in connect : ", $rootScope.user);
 				ctrl.wallet.refreshAllBalances();
 				$rootScope.$emit("loggedIn", '');
 				ctrl.login_done();
 			}, function(error) {
 				$rootScope.toogleError(error.data);
 				console.log(error);
 			});
 		})
 	})
 }

/**
 * Connection via linkedin.
 * @method linkedin_connect
 */
 ctrl.linkedin_connect= function()
 {
 	OAuth.popup('linkedin').done(function(result) {
 		console.log(result)
 		result.me().done(function(userData) {
 			$http.post('/login', {
 				"provider": "linkedin",
 				"socialId": userData.id,
 				"socketid": $rootScope.sessionId
 			}).then(function(response) {
 				console.log("RECEIVED = ", response);
 				sessionStorage.user = JSON.stringify(response.data.user);
 				$sessionStorage.SociethyToken = response.data.token;
 				$sessionStorage.username = response.data.user.name;
 				$rootScope.user = ctrl.user = response.data.user;
				console.log("USER IS SET in connect : ", $rootScope.user);
 				ctrl.wallet.refreshAllBalances();
 				$rootScope.$emit("loggedIn", '');
 				ctrl.login_done();
 			}, function(error) {
 				$rootScope.toogleError(error.data);
 				console.log(error);
 			});
 		})
 	})
 }

/**
 * Connection via github.
 * @method github_connect
 */
 ctrl.github_connect = function ()
 {
 	OAuth.popup('github').done(function(result) {
 		console.log(result)
 		result.me().done(function(userData) {
 			$http.post('/login', {
 				"provider": "github",
 				"socialId": userData.id,
 				"socketid": $rootScope.sessionId
 			}).then(function(response) {
 				console.log("RECEIVED = ", response);
 				sessionStorage.user = JSON.stringify(response.data.user);
 				$sessionStorage.SociethyToken = response.data.token;
 				$sessionStorage.username = response.data.user.name;
 				$rootScope.user = ctrl.user = response.data.user;
				console.log("USER IS SET in connect : ", $rootScope.user);
 				ctrl.wallet.refreshAllBalances();
 				$rootScope.$emit("loggedIn", '');
 				ctrl.login_done();
 			}, function(error) {
 				$rootScope.toogleError(error.data);
 				console.log(error);
 			});
 		})
 	})
 }

/**
 * Connection via google.
 * @method google_connect
 */
 ctrl.google_connect = function ()
 {
 	console.log("hello");
 	res = OAuth.popup('google').done(function(result)
 	{
 		result.me().done(function(userData) {
 			console.log(userData);
 			$http.post('/login', {
 				"provider": "google",
 				"socialId": userData.id,
 				"socketid": $rootScope.sessionId
 			}).then(function(response) {
 				console.log("RECEIVED = ", response);
 				sessionStorage.user = JSON.stringify(response.data.user);
 				$sessionStorage.SociethyToken = response.data.token;
 				$sessionStorage.username = response.data.user.name;
 				$rootScope.user = ctrl.user = response.data.user;
				console.log("USER IS SET in connect : ", $rootScope.user);
 				ctrl.wallet.refreshAllBalances();
 				$rootScope.$emit("loggedIn", '');
 				ctrl.login_done();
 			}, function(error) {
 				$rootScope.toogleError(error.data);
 				console.log(error);
 			});
 		})
 	}).then(function() {}, function(error) {
 		$rootScope.toogleError(error.data);
 		console.log(error);
 	});
 }


 	 $scope.checkPassword = function () {
             if ($scope.form.password.length < 4 || $$scope.form.password.length > 20 ||
                 $$scope.form.password.indexOf(" ") != -1) {
                 $("#passwordCheck").addClass("enabled");
                 $("#passwordCheck").removeClass("disabled");
		 }

}
     $scope.currentStep = 1;

     $scope.form = {
         next: function (form) {
             $scope.toTheTop();

             if (form.$valid) {
                 form.$setPristine();
                 nextStep();
             } else {
                 console.log(form);
                 var field = null, firstError = null;
                 for (field in form) {
                     if (field[0] != '$') {
                         if (firstError === null && !form[field].$valid) {
                             firstError = form[field].$name;
                         }

                         if (form[field].$pristine) {
                             form[field].$dirty = true;
                         }
                     }
                 }
                 console.log(firstError)
                 angular.element('.ng-invalid[name=' + firstError + ']').focus();
                 errorMessage('please complete the form in this step before proceeding');
             }
         },

         prev: function (form) {
             $scope.toTheTop();
             prevStep();
         },

         goTo: function (form, i) {
             if (parseInt($scope.currentStep) > parseInt(i)) {
                 goToStep(i);

             } else {
                 if (form.$valid) {
                     goToStep(i);

                 } else
                     errorMessage('Please complete the form in this step before proceeding');
             }
         },

         submit: function (form) {
                 $http.post('/newUser', {
                     name: $scope.form.username,
                     email: $scope.form.email,
                     password: $scope.form.password,
                     eth: $scope.form.wantsKey || false,
                     firstname: $scope.form.firstname || "",
                     lastname: $scope.form.lastname || "",
                     birthday: $scope.form.birthday || "",
                     gender: $scope.form.gender || "",
                     address: $scope.form.address || "",
                     city: $scope.form.city || "",
                     contact_list: [],
                     socketid: $rootScope.sessionId
                 }).then(function(response) {
                         console.log("RECEIVED = ", response);
                         $sessionStorage.SociethyToken = response.data.token;
                         $rootScope.user = $scope.user = response.data.user;
                         console.log("USER IS SET in register : ", $rootScope.user);
                         $rootScope.$emit("loggedIn", '');
                         $state.go("app.me", ctrl, {reload: true})
                     },
                     function(error) {
                         $rootScope.toogleError(error.data);
                         console.log(error);
                 })
         },

         reset: function () {
         }
     };
     var nextStep = function () {
         $scope.currentStep++;
     };
     var prevStep = function () {
         $scope.currentStep--;
     };
     var goToStep = function (i) {
         $scope.currentStep = i;
     };

     var errorMessage = function (text) {

         ngNotify.set(text, {
             theme: 'pure',
             position: 'top',
             type: 'error',
             button: 'true',
             sticky: false,
             duration: 3000
         });
     };


     var compareTo = function() {
         return {
             require: "ngModel",
             scope: {
                 otherModelValue: "=compareTo"
             },
             link: function(scope, element, attributes, ngModel) {

                 ngModel.$validators.compareTo = function(modelValue) {
                     return modelValue == scope.otherModelValue;
                 };

                 scope.$watch("otherModelValue", function() {
                     ngModel.$validate();
                 });
             }
         };
     };


     app.directive("compareTo", compareTo);



    /*
    ** Handle the modification of the personal informations
    */

    // var over = false;
    // $(".form-group").mouseenter(function() {
    // 	$(this).children(".accountInfo").stop().animate({ width: "93%" }, 600);//.next().stop().animate({ opacity: "1"}, 600, function() {
    // 	//     $(this).css({display: "inline-block"});
    // 	// });
    // 	over = true;
    // });

    // $(".form-group").mouseleave(function() {
    // 	$(this).children(".accountInfo").stop().animate({ width: "99%" }, 600);//.children(".editAccountInfo").stop().fadeOut(500).prev()
    //     over = false;
    // });

    return ctrl;
});
