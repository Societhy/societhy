app.controller('NewsController', function($scope, $rootScope, $http, $sessionStorage, FileUploader ,$state, $controller, $location, socketIO) {
    var ctrl = this;
    console.log("loaded");

    $scope.news_form = {};
    $scope.news_form.text = "";
    $scope.news_form.title = "";


    this.clickOnSubmit = function()
    {
        $http.post('/publish_news', {
            "title": $scope.news_form.title,
            "text": $scope.news_form.text,
            "orga_id": $rootScope.currentOrga._id
        }).then(function(response)
            {
                for (var i = 0; i != uploaderImages.queue.length; i++)
                {
                    console.log(response["data"]["key"])
                    uploaderImages.queue[i].formData.push({"news_key" :response["data"]["news_key"]})
                    uploaderImages.queue[i].formData.push({"orga_id" : $rootScope.currentOrga._id})
                }
                uploaderImages.uploadAll();

            }
            , function(error) {$rootScope.toogleError(error.data);});

    };

    var uploaderImages = $scope.uploaderImages = new FileUploader({
        url: '/publish_news_photo',
        alias: 'pic',
        headers: {
            Authentification: $sessionStorage.SociethyToken
        }
    });

    uploaderImages.filters.push({
        name: 'imageFilter',
        fn: function (item, options) {
            var type = '|' + item.type.slice(item.type.lastIndexOf('/') + 1) + '|';
            return '|jpg|png|jpeg|bmp|gif|'.indexOf(type) !== -1;
        }
    });

    uploaderImages.onErrorItem = function (fileItem, response, status, headers) {
        console.info('onErrorItem', fileItem, response, status, headers);
    };

    uploaderImages.onSuccessItem = function (fileItem, response, status, headers) {
        console.info('SUCCESS', fileItem, response, status, headers);
    }
    return ctrl;
});