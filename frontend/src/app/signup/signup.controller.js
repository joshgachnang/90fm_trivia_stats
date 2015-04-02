'use strict';

angular.module('signup')
  .controller('SignupCtrl', ['$scope', 'Signup', function($scope, Signup) {
    $scope.user = {};
    $scope.register = function() {
      Signup.register($scope.user);
    };
  }]);

