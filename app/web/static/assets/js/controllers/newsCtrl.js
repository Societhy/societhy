app.controller('NewsController', function($scope, $rootScope, $http, $sessionStorage, FileUploader ,$state, $controller, $location, socketIO) {
    var ctrl = this;

    $scope.news_form = {};
    $scope.news_form.text = "";
    $scope.news_form.title = "";
    $scope.news_form.yt = "";
    $scope.imagesource = {};
    var currIndex = 0;


    ctrl.getIframeSrc = function (id)
    {
        console.log("http://www.youtube.com/embed/" + id +"?autoplay=0&origin=http://example.com");
        return "http://www.youtube.com/embed/" + id +"?autoplay=0&origin=http://example.com"
    };

    app.filter('youtubeEmbedUrl', function ($sce) {
        return function (videoId) {
            return $sce.trustAsResourceUrl('http://www.youtube.com/embed/' + videoId);
        };
    });

    this.clickOnSubmit = function()
    {
        $http.post('/publish_news', {
            "title": $scope.news_form.title,
            "text": $scope.news_form.text,
            "yt_url": $scope.news_form.yt,
            "orga_id": $rootScope.currentOrga._id
        }).then(function(response)
            {
                if (uploaderImages.queue.length != 0)
                {
                    for (var i = 0; i != uploaderImages.queue.length; i++) {
                        uploaderImages.queue[i].formData.push({"news_key": response["data"]["news_key"]})
                        uploaderImages.queue[i].formData.push({"orga_id": $rootScope.currentOrga._id})
                    }
                    uploaderImages.uploadAll();
                }
                else
                {
                    $scope.currentOrga = $rootScope.currentOrga = response.data.orga;
                }
            }
            , function(error) {$rootScope.toogleError(error.data);});

    };

    this.loadImage = function (key)
    {
        $http.post('/get_news_photo',
            {
                "orga_id": $rootScope.currentOrga._id,
                "news_key": key
            }
        ).then(function (response) {
            var respdata = response.data;
            $scope.imagesource[key] = [];
            currIndex = 0;
            if (respdata.length > 0) {
                for (var i = 0; i != respdata.length; i++) {
                    $scope.imagesource[key].push({image: respdata[i], id: currIndex++});
                }
            }
        });
    };

    var uploaderImages = $scope.uploaderImages = new FileUploader({
        url: '/publish_news_photo',
        alias: 'pic',
        headers: {
            Authentification: $sessionStorage.SociethyToken
        }
    });

    uploaderImages.onBeforeUploadItem = function (item) {
        item.formData.push({"name": item.file.name});
        item.formData.push({"type": item.file.type});
    };

    uploaderImages.filters.push({
        name: 'imageFilter',
        fn: function (item, options) {
            var type = '|' + item.type.slice(item.type.lastIndexOf('/') + 1) + '|';
            return '|jpg|png|jpeg|bmp|gif|'.indexOf(type) !== -1;
        }
    });

    uploaderImages.onErrorItem = function (fileItem, response, status, headers) {
    };

    uploaderImages.onSuccessItem = function (fileItem, response, status, headers) {
        $scope.currentOrga = $rootScope.currentOrga = response.orga;
    };

    uploaderImages.onCompleteAll = function (fileItem, response, status, headers) {

    };

    return ctrl;
});