SELECT
   id,
   localpath,
   CASE
      WHEN played ISNULL OR skipped ISNULL THEN 0
   ELSE
      CASE
         WHEN (played+skipped>=10) THEN (( CAST(played as real)/(played+skipped))*4.0)
         ELSE 0.5
      END
   END +
      CASE WHEN played ISNULL AND skipped ISNULL THEN 10
      ELSE 0
      END +
   (CASE WHEN lastPlayed ISNULL THEN 604800 ELSE
       julianday('now')*86400 - julianday(lastPlayed)*86400 -- seconds since last play
   END - 604800)/604800*7 +
   CASE WHEN added ISNULL THEN 0 ELSE
      CASE WHEN julianday('now')*86400 - julianday(added)*86400 < 1209600 THEN
         (julianday('now')*86400 - julianday(added)*86400)/1209600*0
      ELSE
         0
      END
   END
      AS score
FROM song s LEFT JOIN channel_song_data rel ON ( rel.song_id == s.id )
ORDER BY score DESC
LIMIT 10 OFFSET 0
;
