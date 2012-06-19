<?php



class JB_Table extends Zend_Db_Table_Abstract
{

    public function getById($id)
    {
        $res = $this->find($id);
        if (count($res) == 0)
            return array();
        return $res[0];
    }



}

