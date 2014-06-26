<?php
namespace Application\View\Helper;

use Zend\View\Helper\AbstractHelper;

/**
 * Returns colored string with status name (human-way)
 *
 */

class HumanReadableBytes extends AbstractHelper
{
    public function __invoke($size, $precision = 2)
    {
        $prefixes = array('', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y');
        $result = $size;
        $index = 0;
        while ($result > 1024 && $index < count($prefixes)) {
            $result = $result / 1024;
            $index++;
        }
        return sprintf('%1.' . $precision . 'f %sB', $result, $prefixes[$index]);

    }
}