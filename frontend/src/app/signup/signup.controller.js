'use strict';

angular.module('signup')
  .controller('SignupCtrl', ['$scope', 'Signup', function($scope, Signup) {
    $scope.user = {
      contactEmail: true,
      contactPhone: true
    };
    $scope.register = function() {
      Signup.register($scope.user);
    };
  }]);

