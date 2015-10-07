'use strict';

var eProWebApp = angular.module('eProWebApp', [
    "ngRoute", 
    "ngResource"
])
.config(function ($interpolateProvider, $httpProvider, $resourceProvider, $routeProvider) {
    // Use square brackets instead of curly brackets as template tags
    $interpolateProvider.startSymbol('[[').endSymbol(']]');

    // CSRF Support
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

    // This only works in angular 3!
    // It makes dealing with Django slashes at the end of everything easier.
    $resourceProvider.defaults.stripTrailingSlashes = false;

    // Django expects jQuery like headers
    // $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8';

    // Routing
    $routeProvider.when('/', {
        templateUrl: '../static/epro/js/app/views/prlist.html',
        controller: 'PurchaseRequestListController',
    }).
    when('/pr', {
        templateUrl: '../static/epro/js/app/views/pr.html',
        controller: 'PurchaseRequestListController',
    }).
    otherwise({ redirectTo: '/' });
});