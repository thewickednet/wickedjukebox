<?php
/**
 * Popularity graph
 *
 * Draws a radial graph representing a positive or negative parametric value
 * (between -1.0 and +1.0)
 *
 * Negative values will have a positive angle (counter-clockwise) and positive
 * values will have a negative angle (clockwise)
 *
 * HTTP-Request parameters:
 *
 *    @param value: The value to represent (-1.0 to 1.0)
 *    @type value:  float
 *
 *    @param radius: The graph radius in pixels (optional, default=5)
 *    @type radius:  int
 *
 *    @param pos_color: The color-code (hex) to be used for positive values (optional, default=00cc00)
 *    @type pos_color: string
 *
 *    @param neg_color: The color-code (hex) to be used for negative values (optional, default=ff0000)
 *    @type neg_color: string
 *
 *    @param bg_color: The background-color (optional, default=eeeeee)
 *    @type bg_color: string
 * 
 */

/** hex2color {{{
 * Parse hex-string to a valid image-color
 *
 * @param $image: A 'gd' image resource pointer
 * @type $image: resource pointer
 *
 * @param $color_string: The string that will be converted to an image-color
 * @type $color_string: string
 */
function hex2color( &$image, $color_string ){

   /* Validate argument */
   if ( !preg_match('/#?[0-9a-fA-F]{6}/', $color_string) ){
      trigger_error( "'$color_string' is not a valid color-string (a valid example would be '00cc00')", E_USER_ERROR );
   }

   /* Trim the optional HTML hex-indicator "#" */
   if ( substr( $color_string, 0 , 1 ) == "#" ) {
      $color_string = substr( $color_string, 1, strlen($color_string) );
   }

   /* split into RGB components */
   $components = sscanf($color_string, '%2x%2x%2x');

   /* allocate the color */
   return imagecolorallocate( $image, $components[0], $components[1], $components[2] );

} // }}}

/** to_float {{{
 * Convert a string to float, while being more restrictive than PHPs floatval method
 *
 * @param $in: The value to be converted
 * @type $in: string
 * @return: The converted float value
 */
function to_float( $in ){
   if (!preg_match( "/^-?\\d+(\\.\\d+)?$/", $in )){
      trigger_error( "'$in' is not a valid float value. A valid example would be '1.0112'.", E_USER_ERROR );
   }
   return floatval( $in );
}
// }}}

/** to_int {{{
 * Convert a string to int, while being more restrictive than PHPs intval method
 *
 * @param $in: The value to be converted
 * @type $in: string
 * @return: The converted int value
 */
function to_int( $in ){
   if (!preg_match( "/^-?\\d+$/", $in )){
      trigger_error( "'$in' is not a valid int value. A valid example would be '2'.", E_USER_ERROR );
   }
   return intval( $in );
}
// }}}

/* -- Initialize variables -- {{{ ----------------------------------------- */

$p = array();

if ( empty( $_REQUEST['value'] ) ){
   trigger_error( "Required parameter 'value' is missing! Check the docs in the source code!", E_USER_ERROR );
} else {
   $p['value'] = to_float( $_REQUEST['value'] );
   if ( $p['value'] < -1.0 || $p['value'] > 1.0 ){
      trigger_error( "Value must lie between -1.0 and 1.0 (current value: {$p['value']})", E_USER_ERROR );
   }
}

if ( empty( $_REQUEST['radius'] ) ){
   $p['radius'] = 5;
} else {
   $p['radius'] = to_int( $_REQUEST['radius'] );
}

$image = imagecreatetruecolor($p['radius']*2, $p['radius']*2 );
//imageantialias($image, true);
ImageAlphaBlending($image, false);
ImageSaveAlpha($image, true);
ImageFill($image, 0, 0, IMG_COLOR_TRANSPARENT);

if ( empty( $_REQUEST['pos_color'] ) ){
   $p['pos_color'] = hex2color( $image, '00cc00' );
} else {
   $p['pos_color'] = hex2color( $image, $_REQUEST['pos_color'] );
}

if ( empty( $_REQUEST['neg_color'] ) ){
   $p['neg_color'] = hex2color( $image, 'ff0000' );
} else {
   $p['neg_color'] = hex2color( $image, $_REQUEST['neg_color'] );
}

if ( empty( $_REQUEST['bg_color'] ) ){
   $p['bg_color'] = hex2color( $image, 'eeeeee' );
} else {
   $p['bg_color'] = hex2color( $image, $_REQUEST['bg_color'] );
}

// }}}

imagefilledarc($image, $p['radius'], $p['radius'], $p['radius']*2, $p['radius']*2, 0, 360, $p['bg_color'], IMG_ARC_PIE);
if ( $p['value'] < 0 ){
   imagefilledarc($image, $p['radius'], $p['radius'], $p['radius']*2, $p['radius']*2, -90+$p['value']*360, -90, $p['neg_color'], IMG_ARC_PIE);
} elseif ($p['value'] > 0)  {
   imagefilledarc($image, $p['radius'], $p['radius'], $p['radius']*2, $p['radius']*2, -90, -90+$p['value']*360, $p['pos_color'], IMG_ARC_PIE);
}

// flush image
header('Content-type: image/png');
imagepng($image);
imagedestroy($image);

/* vim: set foldmethod=marker foldlevel=0: */

