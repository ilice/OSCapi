<?php
ini_set("display_errors", "1");
error_reporting(E_ALL);

require_once( __DIR__ . '/../../../vendor/simpletest/simpletest/autorun.php');

class AllTests extends TestSuite {
    function __construct() {
        parent::__construct();
        $this->addFile(dirname(__FILE__) . '/altitud_test.php');
        //$this->addFile(dirname(__FILE__) . '/api_rest_test.php');
        $this->addFile(dirname(__FILE__) . '/catastro_test.php');
        //$this->addFile(dirname(__FILE__) . '/inforiego_test.php');
    }
}
?>