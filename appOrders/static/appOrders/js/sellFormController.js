'use strict';
let sellFormController = angular.module("sellOrderForm", []).controller("sellOrderFormController", function ($scope) {

    $scope.quantity = 1;
    $scope.type = "Market";
    $scope.limitValue = '';
    $scope.stopValue = '';
    $scope.timeForce = "Day";
    $scope.extendedHours = false;

    $scope.limitvar = false;
    $scope.stopvar = false;
    $scope.requiredLimit = false;
    $scope.requiredStop = false;

    $scope.sharePrice = 0;
    $scope.totalSharePrice = 0;
    $scope.balance = 0;
    $scope.expectedBalance = 0;
    $scope.equity = 0;
    $scope.expectedEquity = 0;

    $scope.typeChange = function ()
    {
        switch ($scope.type)
        {
            case 'Market' :
                $scope.limitvar = false;
                $scope.stopvar = false;
                $scope.requiredLimit = false;
                $scope.requiredStop = false;
                $scope.limitValue = '';
                $scope.stopValue = '';
                $scope.extendedHours = false;
                break;
            case 'Stop' :
                $scope.stopvar = true;
                $scope.limitvar = false;
                $scope.requiredLimit = false;
                $scope.requiredStop = true;
                $scope.limitValue = '';
                $scope.extendedHours = false;
                break;
            case 'Limit' :
                $scope.limitvar = true;
                $scope.requiredLimit = true;
                $scope.stopvar = false;
                $scope.requiredStop = false;
                $scope.stopValue = '';
                if( $scope.timeForce === "Day"){
                    $scope.extendedHours = true;
                }
                break;
            case 'StopLimit' :
                $scope.limitvar = true;
                $scope.stopvar = true;
                $scope.requiredLimit = true;
                $scope.requiredStop = true;
                $scope.extendedHours = false;
                break;

        }
    }

    $scope.extendedHoursChange = function()
    {
        if ($scope.extendedHours === true){
            $scope.type = "Limit";
            $scope.timeForce = "Day";
            $scope.limitvar = true;
            $scope.requiredLimit = true;
            $scope.stopvar = false;
            $scope.stopValue = '';
        }
    }

    $scope.timForceChange = function()
    {
        if ($scope.limitvar === "Limit" && $scope.timeForce === "Day"){
            $scope.extendedHours = true;

        }
        else
            $scope.extendedHours = false;
    }

    $scope.quantityChange = function()
    {
        if( $scope.quantity < 1)
            $scope.quantity = 1;

        $scope.totalSharePrice = ($scope.sharePrice * $scope.quantity).toFixed(2);
        $scope.expectedBalance = ($scope.balance - $scope.totalSharePrice).toFixed(2);
        $scope.expectedEquity = (parseFloat($scope.equity)  + parseFloat($scope.totalSharePrice)).toFixed(2);
    }


});

sellFormController.config(function($locationProvider, $interpolateProvider){
    $locationProvider.html5Mode({enabled:true});
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');
 });