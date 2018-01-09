/**
 * Main controller for organizations.
 * @class OrgaMainController
 */
app.controller("OrgaMainController", function(
  $rootScope,
  $scope,
  $http,
  $sessionStorage,
  $timeout,
  $state,
  $controller,
  $uibModal,
  FileUploader
) {
  var ctrl = this;
  $scope.isMember = false;
  ctrl.wallet = $controller("WalletController");


  $scope.listProducts = [];
  $scope.reviewList = [];
  var slides = ($scope.slides = []);
  var currIndex = 0;

  /**
   * Get the organizations list.
   * @method onLoad
   */
  onLoad = function() {
    $http
      .post("/getOrganization", {
        id: $state.params._id
      })
      .then(
        function(response) {
          if (response.data.orga) {
            $scope.currentOrga = $rootScope.currentOrga = response.data.orga;
            ctrl.projects_number = Object.keys(
              $rootScope.currentOrga.projects
            ).length;
            ctrl.projects_list = Object.values($rootScope.currentOrga.projects);
            ctrl.member_list = Object.values($rootScope.currentOrga.members);
            ctrl.jobs = Object.keys($scope.currentOrga.rights);
          }
          $scope.currentRights = $rootScope.currentRights =
            response.data.rights;
          console.log(
            "current orga & rights",
            $scope.currentOrga,
            $scope.currentRights
          );
          if ($rootScope.user) {
            $scope.isMember =
              $rootScope.user.account in $scope.currentOrga.members;
            ctrl.isCurrentUserInvitedToOrga();
          }
        },
        function(error) {
          $state.go("app.dashboard");
          $rootScope.toogleError("Organization does not exist");
          $rootScope.currentOrga = null;
          $rootScope.currentRights = null;
        }
      );
  };

  ctrl.setProduct = function(product) {
    if (product) {
      $http
        .get("/getProductImages/".concat(product._id.$oid))
        .then(function(response) {
          images = response.data;
          currIndex = 0;
          slides = $scope.slides = [];

          if (images.length > 0) {
            for (var i = 0; i != images.length; i++) {
              slides.push({ image: images[i], id: currIndex++ });
            }
          }
        });
    }
    $scope.currentProd = product;
    if ($scope.currentProd) {
      $scope.reviewList = $scope.currentProd.reviewList;
    }
  };

  var uploaderDocs = ($scope.uploaderDocs = new FileUploader({
    url: "/addOrgaDocuments",
    alias: "doc",
    headers: {
      Authentification: $sessionStorage.SociethyToken
    }
  }));

  uploaderDocs.onAfterAddingFile = function() {
    uploaderDocs.queue[uploaderDocs.queue.length - 1].documentPrivacy = [
      "default"
    ];
  };

  uploaderDocs.onBeforeUploadItem = function(item) {
    item.formData.push({ name: item.file.name });
    item.formData.push({ type: item.file.type });
    item.formData.push({ size: item.file.size / 1024 / 1024 });
    item.formData.push({ privacy: item.documentPrivacy });
    console.info("onBeforeUploadItem", item);
  };

  uploaderDocs.onAfterUploadItem = function(item) {};

  ctrl.uploadNewDocuments = function() {
    for (var i = 0; i != uploaderDocs.queue.length; i++) {
      uploaderDocs.queue[i].formData.push({
        orga_id: $rootScope.currentOrga._id
      });
    }
    uploaderDocs.uploadAll();
  };

  ctrl.sendReview = function() {
    productId = $scope.currentProd._id.$oid;
    console.log(this.review);
    console.log(this.rate);
    reviewPack = {
      review: this.review,
      rate: this.rate,
      date: new Date(),
      user: {
        name: $rootScope.user.name,
        id: $rootScope.user._id
      }
    };

    $http.post("/addReviewToProduct/".concat(productId), reviewPack).then(
      function(response) {
        console.log(response);
        $scope.reviewList.push(reviewPack);
      },
      function(error) {
        console.log(error);
      }
    );
  };

  ctrl.acceptInvit = function() {
    if ($scope.doVerifications()) {
      $scope.completeBlockchainAction(
        function(password) {
          $rootScope.toogleWait("Sending membership");
          $http
            .post("/acceptInvitation", {
              orga_id: $rootScope.currentOrga._id,
              password: password,
              socketid: $rootScope.sessionId
            })
            .then(
              function(data) {},
              function(error) {
                $rootScope.toogleError(error);
              }
            );
        },
        function(data) {
          $scope.currentOrga.members = $rootScope.currentOrga.members =
            data.data.orga.members;
          $scope.currentRights = $rootScope.currentRights = data.data.rights;
          $rootScope.user.organizations.push($rootScope.currentOrga);
          $scope.isMember = true;
        }
      );
    }
  };

  ctrl.isCurrentUserInvitedToOrga = function() {
    // if (typeof $rootScope.user !== 'undefined') {
    //     console.log("hello");
    //     $scope.isInvitedToOrga = false;
    //     return;
    // }
    for (var i = 0; i < $rootScope.user.pending_invitation.length; i++) {
      if ($rootScope.user.pending_invitation[i].type === "organisation") {
        if (
          $rootScope.user.pending_invitation[i].id ===
          $rootScope.currentOrga._id
        ) {
          $scope.isInvitedToOrga = true;
          console.log("user is invited to this orga");
          return;
        }
      }
    }

    console.log("not invited");
    $scope.isInvitedToOrga = false;
  };

  /**
   * Opens the new product modal.
   * @method addNewProduct
   */
  ctrl.addNewProduct = function() {
    var modalInstance = $uibModal.open({
      templateUrl: "static/assets/views/modals/newProduct.html",
      controller: "ProductModalController",
      size: "lg",
      resolve: {
        ctrl: function() {
          return ctrl;
        }
      }
    });

    modalInstance.result.then(
      function() {},
      function() {
        ctrl.loadProducts();
      }
    );
  };

  /**
   * Get the product list for the current organizations.
   * @method loadProducts
   */
  ctrl.loadProducts = function() {
    $http
      .get("/getOrgaProducts/".concat($rootScope.currentOrga._id))
      .then(function(response) {
        if (response.status == 200) {
          $scope.listProducts = JSON.parse(response.data);
          ctrl.setProduct($scope.listProducts[0]);
        }
      });
  };

  /**
   * Join a new organization by it's tag and paying the entrance fee.
   * @param {string} tag - Tag of the organization.
   * @method joinOrga
   */
  ctrl.payMembershipFee = function(tag) {
    $scope.doVerifications(
      $scope.checkMembershipFee(
        function(password) {
          $rootScope.toogleWait("Sending membership");
          $http
            .post("/payMembership", {
              socketid: $rootScope.sessionId,
              orga_id: $rootScope.currentOrga._id,
              donation: {
                amount: $rootScope.currentOrga.funding.membershipAmount
              },
              password: password,
              tag: tag
            })
            .then(
              function(data) {},
              function(error) {
                $rootScope.toogleError(error);
              }
            );
        },
        function(data) {
          if (data.data.orga.members) {
            $scope.currentOrga.members = $rootScope.currentOrga.members =
              data.data.orga.members;
            $scope.currentRights = $rootScope.currentRights = data.data.rights;
            $rootScope.user.organizations.push($rootScope.currentOrga);
            $scope.isMember = true;
          }
        }
      )
    );
  };

  /**6
   * Join a new organization by it's tag.
   * @param {string} tag - Tag of the organization.
   * @method joinOrga
   */
  ctrl.joinOrga = function(tag) {
    if ($scope.doVerifications()) {
      $scope.completeBlockchainAction(
        function(password) {
          $rootScope.toogleWait("Joining...");
          $http
            .post("/joinOrga", {
              socketid: $rootScope.sessionId,
              tag: tag,
              orga_id: $rootScope.currentOrga._id,
              password: password
            })
            .then(
              function(data) {},
              function(error) {
                $rootScope.toogleError(error);
              }
            );
        },
        function(data) {
          $scope.currentOrga.members = $rootScope.currentOrga.members =
            data.data.orga.members;
          $scope.currentRights = $rootScope.currentRights = data.data.rights;
          $rootScope.user.organizations.push($rootScope.currentOrga);
          $scope.isMember = true;
        }
      );
    }
  };

  /**
   * Leave the current organization.
   * @method leaveOrga
   */
  ctrl.leaveOrga = function() {
    if ($scope.doVerifications()) {
      $scope.completeBlockchainAction(
        function(password) {
          $rootScope.toogleWait("Leaving...");
          $http
            .post("/leaveOrga", {
              socketid: $rootScope.sessionId,
              orga_id: $rootScope.currentOrga._id,
              password: password
            })
            .then(
              function(data) {},
              function(error) {
                $rootScope.toogleError(error);
              }
            );
        },
        function(data) {
          $scope.currentOrga.members = $rootScope.currentOrga.members =
            data.data.orga.members;
          $scope.currentRights = $rootScope.currentRights = data.data.rights;
          $scope.isMember = false;
          $rootScope.user.organizations.splice(data.data, 1);
        }
      );
    }
  };

  ctrl.expandProject = function(proj) {
    for (var i = 0; i != ctrl.projects_number; i++) {
      if (proj.address == ctrl.projects_list[i].address) {
        ctrl.projects_list[i].expand = proj.expand == false ? true : false;
      }
    }
  };

  /**
   * Create a project from the organization.
   * @method createProject
   */
  ctrl.createProject = function() {
    if ($scope.doVerifications()) {
      $scope.completeBlockchainAction(
        function(password) {
          $rootScope.toogleWait("Creating project");
          $http
            .post("/createProjectFromOrga", {
              socketid: $rootScope.sessionId,
              orga_id: $rootScope.currentOrga._id,
              newProject: {},
              password: password
            })
            .then(
              function(data) {},
              function(error) {
                $rootScope.toogleError(error);
              }
            );
        },
        function(data) {
          $scope.currentOrga.projects = $rootScope.currentOrga.projects =
            data.data.projects;
          for (var i = 0; i != $scope.currentOrga.projects; i++) {
            $scope.currentOrga.projects.expand = false;
          }
        }
      );
    }
  };

  /**
   * Download a document using its id and name
   * @method downloadDoc
   */
  ctrl.downloadDoc = function(doc_id, doc_name) {
    $http
      .get("/getOrgaUploadedDocument/" + doc_id + "/" + doc_name)
      .then(function(response) {
        console.log(response);
        window.location = "/getOrgaUploadedDocument/" + doc_id + "/" + doc_name;
      });
  };

  /**
   * Make a donation to the organization.
   * @method makeDonation
   */
  ctrl.makeDonation = function() {
    donationAmount = $("#donationAmount").val();
    if (donationAmount > 0 && $scope.doVerifications()) {
      $scope.completeBlockchainAction(
        function(password) {
          $rootScope.toogleWait("Sending donation");
          $http
            .post("/makeDonation", {
              socketid: $rootScope.sessionId,
              orga_id: $rootScope.currentOrga._id,
              donation: { amount: donationAmount },
              password: password
            })
            .then(
              function(data) {},
              function(error) {
                $rootScope.toogleError(error);
              }
            );
        },
        function(data) {
          $scope.currentOrga.balance = $rootScope.currentOrga.balance =
            data.data;
          ctrl.wallet.refreshAllBalances();
        }
      );
    } else {
      $rootScope.toogleError("Donation amount must be more than to 0...");
    }
  };

  $rootScope.$on("loggedIn", function(event, data) {
    console.log("onload loggedin");
    onLoad();
  });

  $timeout(function() {
    $(".donate-button").click(ctrl.makeDonation);
  }, 500);

  onLoad();

  return ctrl;
});

app.controller("ProposalController", function(
  $scope,
  $http,
  $timeout,
  $rootScope,
  $controller,
  $state,
  $uibModal,
  ngNotify
) {
  var ctrl = this;

  $scope.proposal_status = {
    pending: "is waiting for approval.",
    debating: "is currently submitted to the votes.",
    approved: "has been approved.",
    denied: "has been denied."
  };

  $rootScope.$watch("currentOrga", function(_new, _old) {
    if (_new != _old) ctrl.reload();
  });

  ctrl.reload = function() {
    if ($rootScope.currentOrga) {
      ctrl.proposal_number = Object.keys(
        $rootScope.currentOrga.proposals
      ).length;
      ctrl.proposal_list = Object.values($rootScope.currentOrga.proposals);

      for (let i = 0; i != ctrl.proposal_list.length; i++) {
        ctrl.proposal_list[i].expand = false;
        if ($rootScope.user != null) {
          for (let j = 0; j != $rootScope.user.votes.length; j++) {
            if (
              $rootScope.user.votes[j].offer ==
              ctrl.proposal_list[i].destination
            )
              ctrl.proposal_list[i].voted = $rootScope.user.votes[j].vote[0];
          }
        }
      }
    }
  };

  ctrl.proposalLookup = function(item) {
    console.log(item);
    if (item) {
      $scope.proposalLookupName = item.title;
    } else {
      $scope.proposalLookupName = "";
    }
  };

  ctrl.expandProposal = function(proposal) {
    for (let i = 0; i != ctrl.proposal_number; i++) {
      if (proposal.destination == ctrl.proposal_list[i].destination)
        ctrl.proposal_list[i].expand = proposal.expand == false ? true : false;
    }
  };

  ctrl.submitProposal = function(proposal) {
    console.log(proposal);
    if ($rootScope.currentRights.create_proposal == true) {
      $scope.completeBlockchainAction(
        function(password) {
          $rootScope.toogleWait("Creating proposal...");
          $http
            .post("/createProposal", {
              password: password,
              socketid: $rootScope.sessionId,
              orga_id: $rootScope.currentOrga._id,
              offer: proposal.offer.address
            })
            .then(
              function(data) {},
              function(error) {
                $rootScope.toogleError(error);
              }
            );
        },
        function(data) {
          $rootScope.currentOrga = data.data;
          ctrl.proposal_number = Object.keys(
            $rootScope.currentOrga.proposals
          ).length;
          ctrl.proposal_list = Object.values($rootScope.currentOrga.proposals);
        }
      );
    } else {
      $rootScope.toogleError(
        "You don't have the right to turn this offer into a proposal"
      );
    }
  };

  ctrl.submitOffer = function() {
    var modalInstance = $uibModal.open({
      templateUrl: "static/assets/views/modals/newOfferModal.html",
      controller: "OfferModalController",
      size: "lg",
      scope: $scope,
      resolve: {
        ctrl: function() {
          return ctrl;
        }
      }
    });
  };

  ctrl.voteForProposal = function(proposal, vote) {
    if ($rootScope.currentRights.vote_proposal == true) {
      $scope.completeBlockchainAction(
        function(password) {
          $rootScope.toogleWait("Voting...");
          $http
            .post("/voteForProposal", {
              password: password,
              socketid: $rootScope.sessionId,
              orga_id: $rootScope.currentOrga._id,
              proposal_id: proposal.proposal_id,
              vote: vote
            })
            .then(
              function(data) {},
              function(error) {
                $rootScope.toogleError(error);
              }
            );
        },
        function(data) {
          $rootScope.currentOrga = data.data.orga;
          $rootScope.user = data.data.user;
          ctrl.reload();
        }
      );
    } else {
      $rootScope.toogleError(
        "You don't have the right to vote for this proposal..."
      );
    }
  };

  ctrl.refreshProposals = function() {
    if ($rootScope.currentOrga) {
      $http
        .get("/refreshProposals/".concat($rootScope.currentOrga._id))
        .then(function(data) {
          $rootScope.currentOrga = data.data;
          ctrl.reload();
        });
    }
  };

  ctrl.executeProposal = function(proposal) {
    $scope.completeBlockchainAction(
      function(password) {
        $rootScope.toogleWait("Proposal is being executed...");
        $http
          .post("/executeProposal", {
            password: password,
            socketid: $rootScope.sessionId,
            orga_id: $rootScope.currentOrga._id,
            proposal_id: proposal.proposal_id
          })
          .then(
            function(data) {},
            function(error) {
              $rootScope.toogleError(error);
            }
          );
      },
      function(data) {
        $rootScope.currentOrga = data.data;
        delete $rootScope.user.transactions[
          "0x076841d6d0569f6cc2a5e4b69827804d0a599121887de44abea4eaf4bb1b395c"
        ];
        ctrl.reload();
      }
    );
  };

  ctrl.withdrawFundsFromOffer = function(proposal) {
    $scope.completeBlockchainAction(
      function(password) {
        $rootScope.toogleWait("Proposal is being executed...");
        $http
          .post("/withdrawFundsFromOffer", {
            password: password,
            socketid: $rootScope.sessionId,
            orga_id: $rootScope.currentOrga._id,
            offer_id: proposal.offer.contract_id
          })
          .then(
            function(data) {},
            function(error) {
              $rootScope.toogleError(
                "You cannot withdraw less than 0.0001 ether"
              );
            }
          );
      },
      function(data) {
        console.log(data);
        $rootScope.toogleInfo(data.data.withdrawal);
      }
    );
  };
  ctrl.reload();

  return ctrl;
});
