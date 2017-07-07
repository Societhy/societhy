/**
 * Controller for login.
 *
 * @class LoginCtrl
 */

 app.controller('LoginController', function($scope, $rootScope, $http, $sessionStorage, $state, $controller, $location) {

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

    /**
     * REGISTRATION
     * @method register
     */
     ctrl.register = function() {

     	if (ctrl.username && ctrl.password) {
     		$http.post('/newUser', {
     			name: ctrl.username,
     			email: ctrl.email,
     			password: ctrl.password,
     			eth: ctrl.wantsKey || false,
     			firstname: ctrl.firstname || "",
     			lastname: ctrl.lastname || "",
     			birthday: ctrl.birthday || "",
     			gender: ctrl.gender || "",
     			address: ctrl.address || "",
     			city: ctrl.city || "",
     			contact_list: [],
     			socketid: $rootScope.sessionId
     		}).then(function(response) {
     			console.log("RECEIVED = ", response);
     			$sessionStorage.SociethyToken = response.data.token;
     			$rootScope.user = ctrl.user = response.data.user;
				console.log("USER IS SET in register : ", $rootScope.user);
     			$rootScope.$emit("loggedIn", '');
     			$state.go("app.me", ctrl, {reload: true})
     		},
     		function(error) {
     			$rootScope.toogleError(error.data);
     			console.log(error);
     		});
     	}
     };

     function registration_checker() {
     	/* Enable datepicker*/
     	$( function() {
     		$( "#datepicker" ).datepicker();
     	} );

     	step = 1;

     	$("div#stepAdvancement button#btn-prev").on("click", function() {
     		step--;
     		updateDisplay();
     	});

     	$("div#stepAdvancement button#btn-next").on("click", function() {
     		step++;
     		updateDisplay()
     	});

	/**
	 * Enable submit button when all mandatory field are filled.
     * @method updateSubmitButtonState
     */
     function updateSubmitButtonState () {
     	if ($(".formChecker.disabled").length != 4) {
     		$("button#submit").prop("disabled", true);
     		$("#beforeSubmit").show();
     	}
     	else {
     		$("button#submit").prop("disabled", false);
     		$("#beforeSubmit").hide();
     	}
     };

	/**
	 * Enable/Disable previous and next button.
     * @method updateDisplay
     */
     function updateDisplay() {
     	if (step == 1)
     		$("div#stepAdvancement button#btn-prev").prop("disabled", true);
     	else
     		$("div#stepAdvancement button#btn-prev").prop("disabled", false);
     	if (step == $(".registrationDatas").length)
     		$("div#stepAdvancement button#btn-next").prop("disabled", true);
     	else
     		$("div#stepAdvancement button#btn-next").prop("disabled", false);
     	$(".registrationDatas").hide();
     	$(".data" + step).show();
     }

	/*
	** Regex for email check
	*/
	$("form input[type='email']").on("change", function() {
		var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
		if (!re.test($(this).val())) {
			$("#emailCheck").removeClass("disabled");
			$("#emailCheck").addClass("enabled");
		}
		else {
			$("#emailCheck").addClass("disabled");
			$("#emailCheck").removeClass("enabled");
		}
		updateSubmitButtonState();
	});

	/*
	** Check Username format
	*/
	$("form input[name='username']").on("change", function() {
		var re = /^[a-zA-Z0-9_-]{3,20}$/;
		if (!re.test($(this).val())) {
			$("#usernameCheck").addClass("enabled");
			$("#usernameCheck").removeClass("disabled");
		}
		else {
			$("#usernameCheck").addClass("disabled");
			$("#usernameCheck").removeClass("enabled");
		}
		updateSubmitButtonState();
	});

	/*
	** Check the requierment for password
	*/
	$("form input[name='password']").on("change", function() {
		if ($(this).val().length < 4 || $(this).val().length > 20 ||
			$(this).val().indexOf(" ") != -1) {
			$("#passwordCheck").addClass("enabled");
		$("#passwordCheck").removeClass("disabled");
	}
	else {
		$("#passwordCheck").removeClass("enabled");
		$("#passwordCheck").addClass("disabled");
	}
	updateSubmitButtonState();
});

	/*
	** Check if passwords match
	*/
	$("form input[name='password'], form input[name='password_again']").on("change", function() {
		if (($("form input[name='password']").length == 0 || $("form input[name='password_again']").length == 0 ) || $("form input[name='password']").val().length != "" && $("form input[name='password_again']").val() != "" &&
			$("form input[name='password_again']").val() !== $("form input[name='password']").val()) {
			$("#passwordConfirmationCheck").addClass("enabled");
		$("#passwordConfirmationCheck").removeClass("disabled");
	}
	else {
		$("#passwordConfirmationCheck").addClass("disabled");
		$("#passwordConfirmationCheck").removeClass("enabled");
	}
	updateSubmitButtonState();
});
}

registration_checker();


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
