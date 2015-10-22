'use strict';

var eProWebApp = angular.module('eProWebApp', [
    "ngRoute", 
    "ngResource",
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
    // By default, angular sends json-formatted POST request, which django forms do not understand.

    // To make sure Django's request.is_ajax() does not return false for ajax requests
    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    
    // Routing
    $routeProvider.when('/', {
        templateUrl: '../static/epro/js/app/views/prlist.html',
        controller: 'RegionCtrl',
    }).
    when('/pr', {
        templateUrl: '../static/epro/js/app/views/pr.html',
        controller: 'RegionCtrl',
    }).
    when('/prform', {
        templateUrl: '../static/epro/js/app/views/pr.html', //'regionform.html',
        controller: 'PRFormCtrl',
    }).
    otherwise({ redirectTo: '/' });
})
.factory('AuthUser', function() { 
    return {
        id: "{{ user.id|default: '' }}" , // Interacting with Django Templates
    }
});