app.controller('ProjectMainController', function($rootScope, $scope, $http, $sessionStorage, $state) {
  var ctrl = this;

  onLoad = function() {
    $http.post('/getProject', {'id': $state.params.id}).then(function(response) {
      $scope.project = response.data;
      $scope.isMember = $rootScope.user._id in response.data.member;
      // desc = $scope.project.description.replace(/(\r\n|\n|\r)/g,"<br />");
      // $scope.project.description = desc;
    }, function(error) {
      $state.go('app.discoverprojects');
      $rootScope.toogleError("Project does not exist");
    });
  };

  onLoad();
  return ctrl;
});
