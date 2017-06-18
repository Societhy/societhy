app.controller('NewsController', function($scope, $rootScope, $http, $sessionStorage, $state, $controller, $location, socketIO) {
    var ctrl = this;
    console.log("loaded");

    $scope.news_form = {};
    $scope.news_form.text = "";

    this.clickOnSubmit = function()
    {
        console.log($scope.news_form.text);
    };

    return ctrl;
});