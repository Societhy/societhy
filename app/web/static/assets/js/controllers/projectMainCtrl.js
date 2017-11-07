app.controller('ProjectMainController', function($rootScope, $scope, $http, $sessionStorage, $state, $timeout, $controller) {

  var ctrl = this;
  ctrl.wallet = $controller("WalletController");

  onLoad = function() {
    $http.post('/getProject', {'id': $state.params._id}).then(function(response) {
      $rootScope.currentProject = $scope.project = response.data.project;
      $scope.currentRights = response.data.rights;
      if ($rootScope.user) {
        $scope.isMember = $rootScope.user._id in $scope.project.members;
      } else {
        $scope.isMember = false;
      }
      // desc = $scope.project.description.replace(/(\r\n|\n|\r)/g,"<br />");
      // $scope.project.description = desc;
      console.log("RIGHTS AND PROJECT", response.data.rights, response.data.project);
    }, function(error) {
      $state.go('app.discoverprojects');
      $rootScope.toogleError("Project does not exist");
    });
  };

  ctrl.joinProject = function(tag) {
    if ($scope.doVerifications()) {
      $scope.completeBlockchainAction(
        function(password) {
          $rootScope.toogleWait("Joining...");
          $http.post('/joinProject', {
            "socketid": $rootScope.sessionId,
            "tag": "member",
            "proj_id": $scope.project._id,
            "password": password
          }).then(function(data) {}, function(error) {
            $rootScope.toogleError(error);
          });
        },
        function(data) {
          $scope.project.members = data.data.project.members;
          // $rootScope.user.projects.push(data.data.project);
          $rootScope.currentProject.members = $scope.project.members = data.data.project.members;
          $rootScope.currentRights = $scope.currentRights = data.data.rights;
          $rootScope.user.projects.push($rootScope.currentProject);
          $scope.isMember = true;
        });
    }
  }

  ctrl.leaveProject = function() {

    if ($scope.doVerifications()) {
      $scope.completeBlockchainAction(
        function(password) {
          $rootScope.toogleWait("Leaving...");
          $http.post('/leaveProject', {
            "socketid": $rootScope.sessionId,
            "proj_id": $scope.project._id,
            "password": password
          }).then(function(data) {}, function(error) {
            $rootScope.toogleError(error);
          });
        },
        function(data) {
          $scope.project.members = data.data.project.members;
          $scope.isMember = false;
        });
    }
  }

  ctrl.donateToProject = function() {
    donationAmount = $("#donationAmount").val();
    if (donationAmount > 0 && $scope.doVerifications()) {
      $scope.completeBlockchainAction(
        function(password) {
          $rootScope.toogleWait("Sending donation")
          $http.post('/donateToProject', {
            "socketid": $rootScope.sessionId,
            "proj_id": $scope.project._id,
            "donation": {
              "amount": donationAmount
            },
            "password": password
          }).then(function(data) {}, function(error) {
            $rootScope.toogleError(error);
          });
        },
        function(data) {
          $scope.project.balance = data.data;
          ctrl.wallet.refreshAllBalances();
          ctrl.refreshProject();
        })
    } else {
      $rootScope.toogleError("Donation amount must be more than to 0...")
    }
  }

  ctrl.refreshProject = function() {
    if ($rootScope.currentProject) {
      $http.get('/refreshProject/'.concat($rootScope.currentProject._id))
      .then(function(data) {
         $rootScope.currentProject = $scope.project = data.data;
      });
    }
  }


  $timeout(function() {
    $(".donate-button").click(ctrl.donateToProject);
  }, 500);

  onLoad();
  return ctrl;
});

app.controller('ProjectProposalController', function($scope, $http, $timeout, $rootScope, $controller, $state, $uibModal, ngNotify) {
  var ctrl = this;

  $scope.proposal_status = {
    "pending": "is waiting for approval.",
    "debating": "is currently submitted to the votes.",
    "approved": "has been approved.",
    "denied": "has been denied."
  }

  $rootScope.$watch("currentOrga", function(_new, _old) {
    if (_new != _old)
      ctrl.reload();
  })

  ctrl.reload = function() {
    if ($rootScope.currentOrga) {
      ctrl.proposal_number = Object.keys($rootScope.currentOrga.proposals).length;
      ctrl.proposal_list = Object.values($rootScope.currentOrga.proposals);

      for (let i = 0; i != ctrl.proposal_list.length; i++) {
        ctrl.proposal_list[i].expand = false;
        if ($rootScope.user != null) {
          for (let j = 0; j != $rootScope.user.votes.length; j++) {
            if ($rootScope.user.votes[j].offer == ctrl.proposal_list[i].destination)
              ctrl.proposal_list[i].voted = $rootScope.user.votes[j].vote[0];
          }
        }
      }
    }
  }

  ctrl.proposalLookup = function(item) {
    console.log(item);
    if (item) {
      $scope.proposalLookupName = item.title;
    }
    else {
     $scope.proposalLookupName = "";
   }
 }

 ctrl.expandProposal = function(proposal) {
  for (let i = 0; i != ctrl.proposal_number; i++) {
    if (proposal.destination == ctrl.proposal_list[i].destination)
      ctrl.proposal_list[i].expand = (proposal.expand == false ? true : false);
  }
}

ctrl.submitProposal = function(proposal) {
  console.log(proposal);
  if ($rootScope.currentRights.create_proposal == true) {
   $scope.completeBlockchainAction(
    function(password) {
     $rootScope.toogleWait("Creating proposal...")
     $http.post('/createProposal', {
      "password": password,
      "socketid": $rootScope.sessionId,
      "orga_id": $rootScope.currentOrga._id,
      "offer": proposal.offer.address
    }).then(function(data) {}, function(error) { $rootScope.toogleError(error);});
   }, function(data) {
    $rootScope.currentOrga = data.data;
    ctrl.proposal_number = Object.keys($rootScope.currentOrga.proposals).length;
    ctrl.proposal_list = Object.values($rootScope.currentOrga.proposals);
  })
 } else {
   $rootScope.toogleError("You don't have the right to turn this offer into a proposal")
 }
}

ctrl.submitOffer = function() {
  var modalInstance = $uibModal.open({
   templateUrl: "static/assets/views/modals/newOfferModal.html",
   controller: 'OfferModalController',
   size: 'lg',
   scope: $scope,
   resolve: {
    ctrl : function() {
     return ctrl;
   }
 }
});
}

ctrl.voteForProposal = function(proposal, vote) {
  if ($rootScope.currentRights.vote_proposal == true) {
   $scope.completeBlockchainAction(
    function(password) {
     $rootScope.toogleWait("Voting...")
     $http.post('/voteForProposal', {
      "password": password,
      "socketid": $rootScope.sessionId,
      "orga_id": $rootScope.currentOrga._id,
      "proposal_id": proposal.proposal_id,
      "vote": vote
    }).then(function(data) {}, function(error) { $rootScope.toogleError(error);});
   }, function(data) {
    $rootScope.currentOrga = data.data.orga;
    $rootScope.user = data.data.user;
    ctrl.reload();
  })
 } else {
   $rootScope.toogleError("You don't have the right to vote for this proposal...")
 }
}

ctrl.refreshProposals = function() {
  if ($rootScope.currentOrga) {
    $http.get('/refreshProposals/'.concat($rootScope.currentOrga._id))
    .then(function(data) {
     $rootScope.currentOrga = data.data;
     ctrl.reload();
   });
  }
}

ctrl.executeProposal = function(proposal) {
 $scope.completeBlockchainAction(
  function(password) {
   $rootScope.toogleWait("Proposal is being executed...")
   $http.post('/executeProposal', {
    "password": password,
    "socketid": $rootScope.sessionId,
    "orga_id": $rootScope.currentOrga._id,
    "proposal_id": proposal.proposal_id,
  }).then(function(data) {}, function(error) { $rootScope.toogleError(error);});
 }, function(data) {
  $rootScope.currentOrga = data.data;
  delete $rootScope.user.transactions["0x076841d6d0569f6cc2a5e4b69827804d0a599121887de44abea4eaf4bb1b395c"];
  ctrl.reload();
});
}

ctrl.withdrawFundsFromOffer = function(proposal) {
 $scope.completeBlockchainAction(
  function(password) {
   $rootScope.toogleWait("Proposal is being executed...")
   $http.post('/withdrawFundsFromOffer', {
    "password": password,
    "socketid": $rootScope.sessionId,
    "orga_id": $rootScope.currentOrga._id,
    "offer_id": proposal.offer.contract_id,
  }).then(function(data) {}, function(error) { $rootScope.toogleError("You cannot withdraw less than 0.0001 ether");});
 }, function(data) {
  console.log(data);
  $rootScope.toogleInfo(data.data.withdrawal);
});
}
ctrl.reload();

return ctrl;
});
