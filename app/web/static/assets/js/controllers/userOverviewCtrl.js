 app.controller('userOverviewCtrl', function($scope, $http, $timeout) {
 	var ctrl = this;

//Load facebook SDK
window.fbAsyncInit = function() {
	FB.init({
		appId      : '1774766892791379',
		xfbml      : true,
		version    : 'v2.8'
	});
	FB.AppEvents.logPageView();
};

(function(d, s, id){
	var js, fjs = d.getElementsByTagName(s)[0];
	if (d.getElementById(id)) {return;}
	js = d.createElement(s); js.id = id;
	js.src = "//connect.facebook.net/en_US/sdk.js";
	fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));

ctrl.fb_connect = function (argument) {
	FB.login(function(response) {

		if (response.authResponse) {
			console.log('Welcome!  Fetching your information.... ');
            console.log(response); // dump complete info
            access_token = response.authResponse.accessToken; //get access token
            user_id = response.authResponse.userID; //get FB UID

            FB.api('/me', function(response) {
                user_email = response.email; //get user email
          // you can store this data into your database             
      });

        } else {
            //user hit cancel button
            console.log('User cancelled login or did not fully authorize.');

        }
    }, {
    	scope: 'publish_stream,email'
    });

}


});