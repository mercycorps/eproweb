var eProControllers = angular.module('eProWebApp.controllers', []);

eProControllers.controller('RegionCtrl', function RegionCtrl($scope, Region) {
    $scope.regions = {};
    Region.query(function(response) {
        $scope.regions = response;
    });

    $scope.regionSubmit = function(code, name) {
        var region = new Region({code: code, name: name});
        region.$save(function(){
            $scope.regions.unshift(region);
        });
    }
});

eProControllers.controller('PRFormCtrl', function RegionCtrl($scope, PRForm) {
    $scope.form;

    PRForm.getForm()
        .success(function (form) {
            $scope.form = form;
        })
        .error(function (error) {
            $scope.status = "Unable to load form: " + error.message;
        });
});