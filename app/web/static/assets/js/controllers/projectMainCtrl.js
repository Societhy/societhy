app.controller('ProjectMainController', function($rootScope, $scope, $http, $sessionStorage, $state) {
  var ctrl = this;

  onLoad = function() {
    $http.post('/getProject', {'id': $state.params._id}).then(function(response) {
      $scope.project = response.data;
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
