'use strict';

var eProWebApp = angular.module('eProWebApp', [
    "ngRoute", 
    "ngResource",
    'ngSanitize',
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
.directive('chosen', function() {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            //attrs references any attributes on the directive element in html
            //iElement is the actual DOM element of the directive,
            //so you can bind to it with jQuery
            /*
            $(iElement).bxSlider({
                mode: 'fade',
                captions: true
            });
            
             //OR you could use that to find the element inside that needs the plugin
            $(iElement).find('.bx-wrapper').bxSlider({
                mode: 'fade',
                captions: true
            });
            */
            function myFunction() {

                //var movable = document.getElementById('#id_approver1');
                //console.log(element.children());
                //console.log('movable');
  
                
                //$('#id_approver1').select2();
            }
            scope.$on('$viewContentLoaded', myFunction);

        }
    };
})
.factory('AuthUser', function() { 
    return {
        id: "{{ user.id|default: '' }}" , // Interacting with Django Templates
    }
});