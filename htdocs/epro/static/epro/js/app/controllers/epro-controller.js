//var eProControllers = angular.module('eProWebApp');

var eProWebControllers = {}; 
eProWebControllers.RegionCtrl = function ($scope, Region) {
    $scope.regions = {};
    Region.query({ 'code': 'BACCA',})
        .$promise.then(function(response) {
            $scope.regions = response;
        },
        function (error) {
            console.log("Could not fetch regions: " + error.message);
        });

    $scope.regionSubmit = function(code, name) {
        var region = new Region({code: code, name: name});
        region.$save(function(){
            $scope.regions.unshift(region);
        });
    }
};

eProWebControllers.PRFormCtrl = function PRFormCtrl($scope, $sce, $compile, PRForm) {
    $scope.form;

    PRForm.getForm()
        .success(function (form) {
            $scope.form = $sce.trustAsHtml(form);

            $scope.load = function() {
                //console.log($(form).find('select').length);
                
                $(form).find('select').each(function(){
                    //console.log($(this));
                    $(this).select2();
                    //console.log(typeof $(this));
                });
            };
            $scope.load();
            
        })
        .error(function (error) {
            $scope.status = "Unable to load form: " + error.message;
        });
    
};

angular.module('eProWebApp').controller(eProWebControllers);
/*
angular.module('eProWebApp').directive('select', function($compile) {
    var linker = function(scope, element, attr) {
        // update the select when data is loaded
        scope.$watch(attr.chosen, function(oldVal, newVal) {
            element.trigger('chosen:updated');
        });

        // update the select when the model changes
        scope.$watch(attr.ngModel, function() {
            element.trigger('chosen:updated');
        });
        element.select2();
    };

    return {
        restrict: 'E',
        link: function(scope, element, attrs) {
            console.log(element);
            
        }
    };
})
*/


