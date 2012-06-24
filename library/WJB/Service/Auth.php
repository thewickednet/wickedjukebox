<?php

class WJB_Service_Auth implements Zend_Auth_Adapter_Interface {

    public $username;
    public $password;
    public $user;

    const NOT_FOUND_MESSAGE = "The username you entered could not be found.";
    const CREDENTIALS_MESSAGE = "The password you entered is not correct.";
    const UNKNOWN_FAILURE = "Authentication failed for an unknown reason.";

    public function __construct($username, $password) {
        $this->username = $username;
        $this->password = $password;
    }

    /**
     * Zend_Auth hook.
     */
    public function authenticate()
    {
        $doctrine = Zend_Registry::get('doctrine');
        $em = $doctrine->getEntityManager();
        $userRepo = $em->getRepository('\WJB\Entity\User');
        $user = $userRepo->findByUsername($this->username);

        if (count($user) > 0)
            $user = array_shift($user);

        if ($user)
        {
            if (md5($this->password) == $user->getPassword())
            {
                $this->user = $user;
                return $this->success();
            }
            else
                return $this->passwordMismatch();
        }
        else
            return $this->notFound();

    }

    /**
     * Factory for Zend_Auth_Result
     *
     *@param integer    The Result code, see Zend_Auth_Result
     *@param mixed      The Message, can be a string or array
     *@return Zend_Auth_Result
     */
    private function result($code, $messages = array()) {
        if (!is_array($messages)) {
            $messages = array($messages);
        }

        $id = null;

        if ($this->user)
            $id = $this->user->getUsername();

        return new Zend_Auth_Result(
            $code,
            $id,
            $messages
        );
    }

    /**
     * "User not found" wrapper for $this->result()
     */
    public function notFound() {
        return $this->result(Zend_Auth_Result::FAILURE_IDENTITY_NOT_FOUND, self::NOT_FOUND_MESSAGE);
    }

    /**
     * "Password does not match" wrapper for $this->result()
     */
    public function passwordMismatch() {
        return $this->result(Zend_Auth_Result::FAILURE_CREDENTIAL_INVALID, self::CREDENTIALS_MESSAGE);
    }

    /**
     * General or Unknown failure wrapper for $this->result()
     */
    public function failed() {
        return $this->result(Zend_Auth_Result::FAILURE, self::UNKNOWN_FAILURE);
    }

    /**
     * "Success" wrapper for $this->result()
     */
    public function success() {
        return $this->result(Zend_Auth_Result::SUCCESS);
    }
}
