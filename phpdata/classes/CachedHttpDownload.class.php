<?php
/**
 * A very simple class to make HTTP GET requests to download images from a remote
 * host. But only make the actual request if the file is out-of-date.
 *
 * WARNING: This currently only supports .jpg files. It has been written to 
 * cache requests to gravatar.com. Proper handling of the HTTP headers has been 
 * left out in favor of code simplicity.
 *
 * The cache keeps md5-hashes of request URLs, with associated metadata. This
 * keeps the filenames clean, and collisions should be negligable.
 */
class CachedHttpDownload {

    static $cache_dir;

    /**
     * Force download the file at the given URL.
     */
    static function download($url) {
        $headers = get_headers($url, 1);

        if (strpos($headers[0], '200 OK') === False) {
            return false;
        }

        if ($headers['Content-Type'] == 'image/jpeg') {
            $target = sprintf('%s/%s.jpg', CachedHttpDownload::$cache_dir, md5($url));
            file_put_contents($target, file_get_contents($url));
            return true;
        }

        return false;
    }

    /**
     * Returns an accessible URL for the cached file. If the file is too old, or
     * does not exist, try to fetch it. The reason this returns an accessible
     * URL, is because the existing handling of user avatars makes it difficult
     * to handle it differently. And I wanted to avoid to poke too much in the
     * innards of the existing cache system.
     *
     * @param $url The URL to retrieve.
     * @param $default The URL to use when we were unable to get the image.
     * @param $ttl The "Time to live" in seconds (default=600). If a file is 
     * older than this, it will be re-downloaded.
     */
    static function cache_url($url, $default, $ttl=600){

        $cache_file = sprintf('%s/%s.jpg',
            CachedHttpDownload::$cache_dir,
            md5($url));
        if (!file_exists($cache_file) || (time() - filemtime($cache_file) > $ttl)) {
            $successful_download = CachedHttpDownload::download($url);
            if (!$successful_download) {
                return $default;
            }
        }

        return sprintf("/http_cache/%s.jpg", md5($url));
    }

}

CachedHttpDownload::$cache_dir = sprintf('%s/../../htdocs/http_cache', dirname(__FILE__));
