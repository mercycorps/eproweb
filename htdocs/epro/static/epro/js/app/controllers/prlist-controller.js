/*
eProWebApp.controller('PurchaseRequestListController', function($scope){
    $scope.prs = [{'name': 'abc', 'total': '7500'}, {'name': 'def', 'total': '8500'}];
});
*/

angular.module('eProWebApp')
    .controller('PurchaseRequestListController', ['$scope', 'dataFactory', 
        function ($scope, dataFactory) {

    $scope.status;
    $scope.users;
    
    getUsers();

    function getUsers() {
        dataFactory.getUsers()
            .success(function (usrs) { 
                $scope.users = usrs;
            })
            .error(function (error) {
                $scope.status = "Unable to load users data: " + error.message;
            });
    }
}]);