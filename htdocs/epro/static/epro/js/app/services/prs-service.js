angular.module('eProWebApp.services', ['ngResource'])
    .factory('Region', function($resource) {
        return $resource('/api/v1/regions/:id/');
    })
    .factory('Country', function($resource) {
        return $resource('/api/v1/countries/');
    })
    .factory('PRForm', ['$http', function($http) {
        var PRForm = {};
        PRForm.getForm = function() {
            return $http.get('/epro/regionform/');
        }
        return PRForm;
    }]);
