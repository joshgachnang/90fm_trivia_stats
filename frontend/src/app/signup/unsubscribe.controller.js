'use strict';

angular.module('triviastats')
  .controller('UnsubscribeCtrl', ['$scope', '$http', 'Signup', 'BACKEND_SERVER', function ($scope, $http, Signup, BACKEND_SERVER) {
    $scope.formData = {};
    $scope.message = '';

    $scope.unsubscribe = function () {
      Signup.unsubscribe($scope.formData).success(function() {
        $scope.message = 'Successfully unsubscribed';
        $scope.formData = {};
      });
    }

  }]);
