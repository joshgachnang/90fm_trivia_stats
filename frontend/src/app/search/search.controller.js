'use strict';

angular.module('triviastats')
  .controller('SearchCtrl', ['$scope', 'Score', function ($scope, Score) {
    $scope.searchTerm = null;
    $scope.filteredTeams = [];
    $scope.processing = false;

    $scope.query = function () {
      $scope.processing = true;
      $scope.filteredTeams = Score.search($scope.searchTerm);
      $scope.processing = false;
    };

  }]);
