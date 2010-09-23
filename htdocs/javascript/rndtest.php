<?php

$conn = mysql_connect("localhost", "jukebox", "3Z6We7xyQBtFNvhs");
mysql_select_db("jukebox");

function array2table($arr,$width)
   {
   $count = count($arr);
   if($count > 0){
       reset($arr);
       $num = count(current($arr));
       echo "<table align=\"center\" border=\"1\"cellpadding=\"5\" cellspacing=\"0\" width=\"$width\">\n";
       echo "<tr>\n";
       foreach(current($arr) as $key => $value){
           echo "<th>";
           echo $key."&nbsp;";
           echo "</th>\n";  
           }  
       echo "</tr>\n";
       while ($curr_row = current($arr)) {
           echo "<tr>\n";
           $col = 1;
           while (false !== ($curr_field = current($curr_row))) {
               echo "<td>";
               echo $curr_field."&nbsp;";
               echo "</td>\n";
               next($curr_row);
               $col++;
               }
           while($col <= $num){
               echo "<td>&nbsp;</td>\n";
               $col++;      
           }
           echo "</tr>\n";
           next($arr);
           }
       echo "</table>\n";
       }
   }

?>


<html>
<head></head>
<body>

<form action="<?= $_SERVER["PHP_SELF"] ?>" method="POST">

Last played: <input type="text" name="lastPlayed" value="<?= (isset($_REQUEST["lastPlayed"]) ? $_REQUEST["lastPlayed"] : 10) ?>" /> <br />
Never Played: <input type="text" name="neverPlayed" value="<?= (isset($_REQUEST["neverPlayed"]) ? $_REQUEST["neverPlayed"] : 13) ?>" /> <br />
User Rating: <input type="text" name="userRating" value="<?= (isset($_REQUEST["userRating"]) ? $_REQUEST["userRating"] : 3) ?>" /> <br />
Proof of Life: <input type="text" name="proofoflife" value="<?= (isset($_REQUEST["proofoflife"]) ? $_REQUEST["proofoflife"] : 180) ?>" /> <br />
Randomness: <input type="text" name="randomness" value="<?= (isset($_REQUEST["randomness"]) ? $_REQUEST["randomness"] : 5) ?>" /> <br />
Song Age: <input type="text" name="songAge" value="<?= (isset($_REQUEST["songAge"]) ? $_REQUEST["songAge"] : 0) ?>" /> <br />
Max random duration: <input type="text" name="max_random_duration" value="<?= (isset($_REQUEST["max_random_duration"]) ? $_REQUEST["max_random_duration"] : 600) ?>" /> <br />
<hr />
Show # results: <input type="text" name="numresults" value="<?= (isset($_REQUEST["numresults"]) ? $_REQUEST["numresults"] : 2) ?>" /> <br />
<input type="submit" />

</form>

<?php
$query = sprintf("
     SELECT s.id, s.localpath, lastPlayed,

        ((IFNULL( least(604800, time_to_sec(timediff(NOW(), lastPlayed))), 604800)-604800)/604800*%d) AS lastPlayedScore,
        ((IFNULL(ls.loves,0)) / (SELECT COUNT(*) FROM users WHERE UNIX_TIMESTAMP(proof_of_life)+%d > UNIX_TIMESTAMP(NOW())) * %d) AS user_rating,
        IF( lastPlayed IS NULL, %d, 0) AS neverPlayed,
        IFNULL( IF( time_to_sec(timediff(NOW(),s.added))<1209600, time_to_sec(timediff(NOW(),s.added))/1209600*%d, 0), 0) AS songAge,

        ((IFNULL( least(604800, time_to_sec(timediff(NOW(), lastPlayed))), 604800)-604800)/604800*%d)
           + ((IFNULL(ls.loves,0)) / (SELECT COUNT(*) FROM users WHERE UNIX_TIMESTAMP(proof_of_life)+%d > UNIX_TIMESTAMP(NOW())) * %d)
           + IF( lastPlayed IS NULL, %d, 0)
           + IFNULL( IF( time_to_sec(timediff(NOW(),s.added))<1209600, time_to_sec(timediff(NOW(),s.added))/1209600*%d, 0), 0)
           + ((RAND()*%f*2)-%f)
        AS score
     FROM song s
        LEFT JOIN channel_song_data c ON (c.song_id=s.id)
        LEFT JOIN (SELECT song_id, COUNT(*) AS loves FROM user_song_standing INNER JOIN users ON(users.id=user_song_standing.user_id) WHERE standing='love' AND UNIX_TIMESTAMP(proof_of_life)+%d > UNIX_TIMESTAMP(NOW()) GROUP BY song_id) ls ON (s.id=ls.song_id)
        LEFT JOIN (SELECT song_id, COUNT(*) AS hates FROM user_song_standing INNER JOIN users ON(users.id=user_song_standing.user_id) WHERE standing='hate' AND UNIX_TIMESTAMP(proof_of_life)+%d > UNIX_TIMESTAMP(NOW()) GROUP BY song_id) hs ON (s.id=hs.song_id)
        INNER JOIN artist a ON ( a.id = s.artist_id )
        INNER JOIN album b ON ( b.id = s.album_id )
     WHERE IFNULL(hs.hates,0) = 0 AND NOT s.broken AND duration < %d
     ORDER BY score DESC
     LIMIT 1
  ",

  mysql_real_escape_string($_REQUEST['lastPlayed']),
  mysql_real_escape_string($_REQUEST['proofoflife']),
  mysql_real_escape_string($_REQUEST['userRating']),
  mysql_real_escape_string($_REQUEST['neverPlayed']),
  mysql_real_escape_string($_REQUEST['songAge']),

  mysql_real_escape_string($_REQUEST['lastPlayed']),
  mysql_real_escape_string($_REQUEST['proofoflife']),
  mysql_real_escape_string($_REQUEST['userRating']),
  mysql_real_escape_string($_REQUEST['neverPlayed']),
  mysql_real_escape_string($_REQUEST['songAge']),
  mysql_real_escape_string($_REQUEST['randomness']),
  mysql_real_escape_string($_REQUEST['randomness']),

  mysql_real_escape_string($_REQUEST['proofoflife']),
  mysql_real_escape_string($_REQUEST['proofoflife']),
  mysql_real_escape_string($_REQUEST['max_random_duration'])
  );

for ($i=0; $i<(isset($_REQUEST['numresults']) ? $_REQUEST['numresults'] : 1); $i++){
   $result = mysql_query($query);
   if (!$result) {
       die('Invalid query: ' . mysql_error());
   }

   $array = array();
   while($row = mysql_fetch_assoc($result)){ $array[] = $row; }


   array2table($array,600);
}

mysql_close($conn);

?>



<h1>Query</h1>
<pre><?=$query?></pre>


</body>
</html>
