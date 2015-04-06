'use strict';

angular.module('signup', [])
  .service('Signup', ['$http', '$q', 'BACKEND_SERVER', function ($http, $q, BACKEND_SERVER) {
    var service = {};

    service.register = function (postData) {
      // postData should container 'username', 'password' and other required field
      // required fields are defined by the Django User object.
      var deferred = $q.defer();
      $http.post(BACKEND_SERVER + 'auth/register', postData).success(function (data, status, headers, config) {
        console.log('register success', data);
        // Convert checkboxes to valid choice
        var contactMethod = 'none';
        if (postData.contactEmail === true && postData.contactPhone) {
          contactMethod = 'both';
        }
        else if (postData.contactEmail === true) {
          contactMethod = 'email'
        }
        else if (postData.contactPhone === true) {
          contactMethod = 'text'
        }
        // If we have profile data, update the user profile
        if (postData.teamName !== undefined || postData.phoneNumber !== undefined) {
          var profileData = {
            'team_name': postData.teamName,
            'phone_number': postData.phoneNumber,
            'contact_method': contactMethod
          };
          $http.put(BACKEND_SERVER + 'users/' + data.id + '/', profileData)
            .success(function (data) {
              deferred.resolve(data);
            })
            .error(function (g) {
              deferred.reject();
            });
          return;
        }
        deferred.resolve();
      }).error(function () {
        deferred.reject();
      });
      return deferred.promise;
    };

    return service;
  }]);
