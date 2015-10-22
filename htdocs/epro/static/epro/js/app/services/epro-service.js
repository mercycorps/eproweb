angular.module('eProWebApp')
    .factory('Region', function($resource) {
        return $resource('/api/v1/regions/:id/');
    })
    .factory('Country', function($resource) {
        return $resource('/api/v1/countries/:id/');
    })
    .factory('Office', function($resource) {
        return $resource('/api/v1/offices/:id/');
    })
    .factory('Currency', function($resource) {
        return $resource('/api/v1/currencies/:id/');
    })
    .factory('PRForm', ['$http', function($http) {
        var PRForm = {};
        PRForm.getForm = function() {
            return $http.get('/epro/regionform/');
        }
        return PRForm;
    }]);
