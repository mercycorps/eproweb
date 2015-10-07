angular.module('eProWebApp')
    .factory('dataFactory', ['$http', function($http) {

        var urlBase = '/api/v1/users/';
        var dataFactory = {};

        dataFactory.getUsers = function() {
            return $http.get(urlBase);
        };
        
        
        
        return dataFactory;
    }]);
/*
eProWebApp.factory('PurchaseRequestService', function ($http, $q) {
    var api_url = "/api/v1/users/";
    return {
        get: function (pr_id) {
            var url = api_url + pr_id + "/";
            var defer = $q.defer();
            $http({method: 'GET', url: url}).
                success(function (data, status, headers, config) {
                    defer.resolve(data);
                })
                .error(function (data, status, headers, config) {
                    defer.reject(status);
                });
            return defer.promise;
        },
        list: function () {
            var defer = $q.defer();
            $http({method: 'GET', url: api_url}).
                success(function (data, status, headers, config) {
                    defer.resolve(data);
                }).error(function (data, status, headers, config) {
                    defer.reject(status);
                });
            return defer.promise;
        },
        update: function (purchase_request) {
            var url = api_url + purchase_request.id + "/";
            var defer = $q.defer();
            $http({method: 'PUT',
                url: url,
                data: purchase_request}).
                success(function (data, status, headers, config) {
                    defer.resolve(data);
                }).error(function (data, status, headers, config) {
                    defer.reject(status);
                });
            return defer.promise;
        },
        save: function (purchase_request) {
            var url = api_url;
            var defer = $q.defer();
            $http({method: 'POST',
                url: url,
                data: purchase_request}).
                success(function (data, status, headers, config) {
                    defer.resolve(data);
                }).error(function (data, status, headers, config) {
                    defer.reject(status);
                });
            return defer.promise;
        },
    }
});
*/