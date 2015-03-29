'use strict';

angular.module('triviastats')
  .service('Score', ['djResource', '$q', '$http', 'BACKEND_SERVER', function (djResource, $q, $http, BACKEND_SERVER) {
    var service = {};
    console.log(BACKEND_SERVER + 'scores\/');
    var api = djResource(BACKEND_SERVER + 'scores\/');
    var teamsApi = djResource(BACKEND_SERVER + 'teams\/');
    //$http.get(BACKEND_SERVER + 'scores\/')

    service.teamScores = function (team, year) {
      return api.query({
        'team_name': team,
        'ordering': '-year,team_name,-hour',
        'year': year
      });
    };

    service.hourScores = function (hour, year) {
      if (year === undefined) {
        year = new Date().getFullYear();
      }
      return api.query({
        'ordering': '-score',
        'hour': hour,
        'year': year
      });
    };

    service.search = function (searchString) {
      return api.query({
        // User team name to keep them grouped properly
        'ordering': '-year,team_name,-hour',
        'search': searchString
      });
    };

    service.teamList = function () {
      return teamsApi.query({});
    };

    return service;
  }]);
