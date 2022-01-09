Search.setIndex({docnames:["appendix/api/modules","appendix/api/wickedjukebox","appendix/api/wickedjukebox.cli","appendix/api/wickedjukebox.component","appendix/api/wickedjukebox.core","appendix/api/wickedjukebox.model","appendix/api/wickedjukebox.model.db","appendix/api/wickedjukebox.smartplaylist","appendix/mpd-in-docker","configuration","index","installation","maintenance","modules/autoplay","modules/ipc","modules/jingle","modules/player","modules/queue","usage"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":4,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":3,"sphinx.domains.rst":2,"sphinx.domains.std":2,sphinx:56},filenames:["appendix/api/modules.rst","appendix/api/wickedjukebox.rst","appendix/api/wickedjukebox.cli.rst","appendix/api/wickedjukebox.component.rst","appendix/api/wickedjukebox.core.rst","appendix/api/wickedjukebox.model.rst","appendix/api/wickedjukebox.model.db.rst","appendix/api/wickedjukebox.smartplaylist.rst","appendix/mpd-in-docker.rst","configuration.rst","index.rst","installation.rst","maintenance.rst","modules/autoplay.rst","modules/ipc.rst","modules/jingle.rst","modules/player.rst","modules/queue.rst","usage.rst"],objects:{"":[[1,0,0,"-","wickedjukebox"]],"wickedjukebox.channel":[[1,1,1,"","Channel"]],"wickedjukebox.channel.Channel":[[1,2,1,"","run"],[1,2,1,"","tick"]],"wickedjukebox.cli":[[2,0,0,"-","jukebox_admin"],[2,0,0,"-","run_channel"]],"wickedjukebox.cli.jukebox_admin":[[2,3,1,"","main"],[2,3,1,"","parse_args"],[2,3,1,"","process_rescan"]],"wickedjukebox.cli.run_channel":[[2,3,1,"","main"],[2,3,1,"","make_channel"],[2,3,1,"","parse_args"]],"wickedjukebox.component":[[3,3,1,"","get_autoplay"],[3,3,1,"","get_ipc"],[3,3,1,"","get_jingle"],[3,3,1,"","get_player"],[3,3,1,"","get_queue"],[3,0,0,"-","ipc"],[3,0,0,"-","jingle"],[3,3,1,"","make_component_getter"],[3,0,0,"-","player"],[3,0,0,"-","queue"],[3,0,0,"-","random"]],"wickedjukebox.component.ipc":[[3,1,1,"","AbstractIPC"],[3,1,1,"","Command"],[3,1,1,"","DBIPC"],[3,1,1,"","FSIPC"],[3,1,1,"","FSStateFiles"],[3,6,1,"","InvalidCommand"],[3,7,1,"","LOG"],[3,1,1,"","NullIPC"]],"wickedjukebox.component.ipc.AbstractIPC":[[3,4,1,"","CONFIG_KEYS"],[3,2,1,"","configure"],[3,2,1,"","get"],[3,2,1,"","set"]],"wickedjukebox.component.ipc.Command":[[3,4,1,"","SKIP"]],"wickedjukebox.component.ipc.DBIPC":[[3,2,1,"","get"],[3,2,1,"","set"]],"wickedjukebox.component.ipc.FSIPC":[[3,4,1,"","CONFIG_KEYS"],[3,2,1,"","configure"],[3,2,1,"","get"],[3,5,1,"","root"],[3,2,1,"","set"]],"wickedjukebox.component.ipc.FSStateFiles":[[3,4,1,"","SKIP_REQUESTED"]],"wickedjukebox.component.ipc.NullIPC":[[3,2,1,"","get"],[3,2,1,"","set"]],"wickedjukebox.component.jingle":[[3,1,1,"","AbstractJingle"],[3,1,1,"","FileBasedJingles"],[3,1,1,"","NullJingle"]],"wickedjukebox.component.jingle.AbstractJingle":[[3,4,1,"","CONFIG_KEYS"],[3,2,1,"","configure"],[3,2,1,"","pick"]],"wickedjukebox.component.jingle.FileBasedJingles":[[3,4,1,"","CONFIG_KEYS"],[3,2,1,"","configure"],[3,2,1,"","pick"]],"wickedjukebox.component.jingle.NullJingle":[[3,2,1,"","configure"],[3,2,1,"","pick"]],"wickedjukebox.component.player":[[3,1,1,"","AbstractPlayer"],[3,1,1,"","MpdPlayer"],[3,1,1,"","NullPlayer"],[3,1,1,"","PathMap"]],"wickedjukebox.component.player.AbstractPlayer":[[3,4,1,"","CONFIG_KEYS"],[3,2,1,"","configure"],[3,2,1,"","enqueue"],[3,5,1,"","is_empty"],[3,5,1,"","is_playing"],[3,2,1,"","play"],[3,5,1,"","remaining_seconds"],[3,2,1,"","skip"]],"wickedjukebox.component.player.MpdPlayer":[[3,4,1,"","CONFIG_KEYS"],[3,2,1,"","configure"],[3,2,1,"","connect"],[3,2,1,"","enqueue"],[3,5,1,"","is_empty"],[3,5,1,"","is_playing"],[3,2,1,"","jukebox2mpd"],[3,2,1,"","mpd2jukebox"],[3,2,1,"","play"],[3,5,1,"","remaining_seconds"],[3,2,1,"","skip"]],"wickedjukebox.component.player.NullPlayer":[[3,4,1,"","CONFIG_KEYS"],[3,2,1,"","configure"],[3,2,1,"","enqueue"],[3,5,1,"","is_empty"],[3,5,1,"","is_playing"],[3,2,1,"","play"],[3,5,1,"","remaining_seconds"],[3,2,1,"","skip"]],"wickedjukebox.component.player.PathMap":[[3,4,1,"","jukebox_path"],[3,4,1,"","mpd_path"]],"wickedjukebox.component.queue":[[3,1,1,"","AbstractQueue"],[3,1,1,"","DatabaseQueue"],[3,1,1,"","NullQueue"]],"wickedjukebox.component.queue.AbstractQueue":[[3,4,1,"","CONFIG_KEYS"],[3,2,1,"","configure"],[3,2,1,"","dequeue"]],"wickedjukebox.component.queue.DatabaseQueue":[[3,2,1,"","dequeue"]],"wickedjukebox.component.queue.NullQueue":[[3,2,1,"","dequeue"]],"wickedjukebox.component.random":[[3,1,1,"","AbstractRandom"],[3,1,1,"","AllFilesRandom"],[3,1,1,"","NullRandom"],[3,1,1,"","SmartPrefetch"],[3,1,1,"","SmartPrefetchThread"]],"wickedjukebox.component.random.AbstractRandom":[[3,4,1,"","CONFIG_KEYS"],[3,2,1,"","configure"],[3,2,1,"","pick"]],"wickedjukebox.component.random.AllFilesRandom":[[3,4,1,"","CONFIG_KEYS"],[3,2,1,"","configure"],[3,2,1,"","pick"]],"wickedjukebox.component.random.NullRandom":[[3,2,1,"","configure"],[3,2,1,"","pick"]],"wickedjukebox.component.random.SmartPrefetch":[[3,4,1,"","CONFIG_KEYS"],[3,2,1,"","configure"],[3,2,1,"","pick"]],"wickedjukebox.component.random.SmartPrefetchThread":[[3,4,1,"","daemon"],[3,2,1,"","run"]],"wickedjukebox.config":[[1,1,1,"","Config"],[1,1,1,"","ConfigKeys"],[1,1,1,"","ConfigOption"],[1,1,1,"","ConfigScope"],[1,1,1,"","Sentinel"],[1,3,1,"","default_config"]],"wickedjukebox.config.Config":[[1,2,1,"","dictify"],[1,2,1,"","get"],[1,2,1,"","get_section"],[1,2,1,"","load_config"]],"wickedjukebox.config.ConfigKeys":[[1,4,1,"","AUTOPLAY"],[1,4,1,"","DSN"],[1,4,1,"","IPC"],[1,4,1,"","JINGLE"],[1,4,1,"","PLAYER"],[1,4,1,"","QUEUE"]],"wickedjukebox.config.ConfigOption":[[1,4,1,"","scope"],[1,4,1,"","section"],[1,4,1,"","subsection"]],"wickedjukebox.config.ConfigScope":[[1,4,1,"","CHANNEL"],[1,4,1,"","CORE"]],"wickedjukebox.core":[[4,0,0,"-","smartfind"]],"wickedjukebox.core.smartfind":[[4,7,1,"","LAST_PLAYED_CUTOFF"],[4,7,1,"","SONG_AGE_CUTOFF"],[4,1,1,"","ScoringConfig"],[4,3,1,"","find_song"],[4,3,1,"","get_standing_query"],[4,3,1,"","score_expression"],[4,3,1,"","smart_random_no_users"],[4,3,1,"","smart_random_with_users"]],"wickedjukebox.core.smartfind.ScoringConfig":[[4,4,1,"","LAST_PLAYED"],[4,4,1,"","MAX_DURATION"],[4,4,1,"","NEVER_PLAYED"],[4,4,1,"","PROOF_OF_LIFE_TIMEOUT"],[4,4,1,"","RANDOMNESS"],[4,4,1,"","SONG_AGE"],[4,4,1,"","USER_RATING"]],"wickedjukebox.exc":[[1,6,1,"","ConfigError"],[1,6,1,"","WickedJukeboxException"]],"wickedjukebox.logutil":[[1,3,1,"","caller_source"],[1,3,1,"","qualname"],[1,3,1,"","qualname_repr"],[1,3,1,"","setup_logging"]],"wickedjukebox.model":[[5,0,0,"-","audiometa"],[6,0,0,"-","db"]],"wickedjukebox.model.audiometa":[[5,1,1,"","AudioMeta"],[5,1,1,"","MP3Meta"],[5,1,1,"","MetaFactory"],[5,3,1,"","display_file"],[5,3,1,"","main"]],"wickedjukebox.model.audiometa.AudioMeta":[[5,2,1,"","get_album"],[5,2,1,"","get_artist"],[5,2,1,"","get_bitrate"],[5,2,1,"","get_comment"],[5,2,1,"","get_duration"],[5,2,1,"","get_genres"],[5,2,1,"","get_release_date"],[5,2,1,"","get_title"],[5,2,1,"","get_total_tracks"],[5,2,1,"","get_track_no"],[5,2,1,"","items"],[5,2,1,"","keys"],[5,2,1,"","values"]],"wickedjukebox.model.audiometa.MP3Meta":[[5,2,1,"","decode_text"],[5,2,1,"","get_album"],[5,2,1,"","get_artist"],[5,2,1,"","get_bitrate"],[5,2,1,"","get_duration"],[5,2,1,"","get_genres"],[5,2,1,"","get_release_date"],[5,2,1,"","get_title"],[5,2,1,"","get_total_tracks"],[5,2,1,"","get_track_no"]],"wickedjukebox.model.audiometa.MetaFactory":[[5,2,1,"","create"]],"wickedjukebox.model.db":[[6,0,0,"-","auth"],[6,0,0,"-","events"],[6,0,0,"-","lastfm"],[6,0,0,"-","library"],[6,0,0,"-","logging"],[6,0,0,"-","playback"],[6,0,0,"-","sameta"],[6,0,0,"-","settings"],[6,0,0,"-","stats"],[6,0,0,"-","webui"]],"wickedjukebox.model.db.auth":[[6,1,1,"","AuthGroup"],[6,1,1,"","AuthGroupPermission"],[6,1,1,"","AuthPermission"],[6,1,1,"","AuthUser"],[6,1,1,"","AuthUserGroup"],[6,1,1,"","AuthUserUserPermission"],[6,1,1,"","Group"],[6,1,1,"","User"]],"wickedjukebox.model.db.auth.AuthGroup":[[6,4,1,"","id"],[6,4,1,"","name"]],"wickedjukebox.model.db.auth.AuthGroupPermission":[[6,4,1,"","group"],[6,4,1,"","group_id"],[6,4,1,"","id"],[6,4,1,"","permission"],[6,4,1,"","permission_id"]],"wickedjukebox.model.db.auth.AuthPermission":[[6,4,1,"","codename"],[6,4,1,"","content_type"],[6,4,1,"","content_type_id"],[6,4,1,"","id"],[6,4,1,"","name"]],"wickedjukebox.model.db.auth.AuthUser":[[6,4,1,"","date_joined"],[6,4,1,"","email"],[6,4,1,"","first_name"],[6,4,1,"","id"],[6,4,1,"","is_active"],[6,4,1,"","is_staff"],[6,4,1,"","is_superuser"],[6,4,1,"","last_login"],[6,4,1,"","last_name"],[6,4,1,"","password"],[6,4,1,"","username"]],"wickedjukebox.model.db.auth.AuthUserGroup":[[6,4,1,"","group"],[6,4,1,"","group_id"],[6,4,1,"","id"],[6,4,1,"","user"],[6,4,1,"","user_id"]],"wickedjukebox.model.db.auth.AuthUserUserPermission":[[6,4,1,"","id"],[6,4,1,"","permission"],[6,4,1,"","permission_id"],[6,4,1,"","user"],[6,4,1,"","user_id"]],"wickedjukebox.model.db.auth.Group":[[6,4,1,"","admin"],[6,4,1,"","id"],[6,4,1,"","nocredits"],[6,4,1,"","queue_add"],[6,4,1,"","queue_remove"],[6,4,1,"","queue_skip"],[6,4,1,"","title"]],"wickedjukebox.model.db.auth.User":[[6,4,1,"","IP"],[6,4,1,"","added"],[6,4,1,"","channel_id"],[6,4,1,"","cookie"],[6,4,1,"","credits"],[6,4,1,"","django_user_id"],[6,4,1,"","downloads"],[6,4,1,"","email"],[6,4,1,"","fullname"],[6,4,1,"","group"],[6,4,1,"","group_id"],[6,4,1,"","id"],[6,4,1,"","lifetime"],[6,4,1,"","password"],[6,4,1,"","picture"],[6,4,1,"","pinnedIp"],[6,4,1,"","proof_of_life"],[6,4,1,"","proof_of_listening"],[6,4,1,"","selects"],[6,4,1,"","skips"],[6,4,1,"","username"],[6,4,1,"","votes"]],"wickedjukebox.model.db.events":[[6,1,1,"","Event"]],"wickedjukebox.model.db.events.Event":[[6,4,1,"","enddate"],[6,4,1,"","id"],[6,4,1,"","lat"],[6,4,1,"","lon"],[6,4,1,"","startdate"],[6,4,1,"","title"]],"wickedjukebox.model.db.lastfm":[[6,1,1,"","LastfmQueue"]],"wickedjukebox.model.db.lastfm.LastfmQueue":[[6,4,1,"","queue_id"],[6,4,1,"","song"],[6,4,1,"","song_id"],[6,4,1,"","time_played"],[6,4,1,"","time_started"]],"wickedjukebox.model.db.library":[[6,1,1,"","Album"],[6,1,1,"","Artist"],[6,1,1,"","Collection"],[6,1,1,"","CollectionhasSong"],[6,1,1,"","Country"],[6,1,1,"","Genre"],[6,1,1,"","Playlist"],[6,1,1,"","PlaylistHasSong"],[6,1,1,"","Song"],[6,1,1,"","SongHasGenre"],[6,1,1,"","SongHasTag"],[6,1,1,"","StandingEnum"],[6,1,1,"","Tag"],[6,1,1,"","UserSongStanding"]],"wickedjukebox.model.db.library.Album":[[6,4,1,"","added"],[6,4,1,"","artist"],[6,4,1,"","artist_id"],[6,2,1,"","by_name"],[6,4,1,"","coverart"],[6,4,1,"","downloaded"],[6,4,1,"","id"],[6,4,1,"","lastfm_mbid"],[6,4,1,"","lastfm_url"],[6,4,1,"","name"],[6,4,1,"","path"],[6,4,1,"","release_date"],[6,4,1,"","type"]],"wickedjukebox.model.db.library.Artist":[[6,4,1,"","added"],[6,4,1,"","bio"],[6,2,1,"","by_name"],[6,4,1,"","country"],[6,4,1,"","id"],[6,4,1,"","lastfm_mbid"],[6,4,1,"","lastfm_url"],[6,4,1,"","name"],[6,4,1,"","photo"],[6,4,1,"","summary"],[6,4,1,"","website"],[6,4,1,"","wikipage"]],"wickedjukebox.model.db.library.Collection":[[6,4,1,"","id"],[6,4,1,"","is_active"],[6,4,1,"","name"],[6,4,1,"","user_id"]],"wickedjukebox.model.db.library.CollectionhasSong":[[6,4,1,"","collection_id"],[6,4,1,"","id"],[6,4,1,"","last_played"],[6,4,1,"","position"],[6,4,1,"","song_id"]],"wickedjukebox.model.db.library.Country":[[6,4,1,"","country_code"],[6,4,1,"","country_name"]],"wickedjukebox.model.db.library.Genre":[[6,4,1,"","added"],[6,2,1,"","by_name"],[6,4,1,"","id"],[6,4,1,"","name"]],"wickedjukebox.model.db.library.Playlist":[[6,4,1,"","id"],[6,4,1,"","name"],[6,4,1,"","probability"],[6,4,1,"","user_id"]],"wickedjukebox.model.db.library.PlaylistHasSong":[[6,4,1,"","playlist_id"],[6,4,1,"","song_id"]],"wickedjukebox.model.db.library.Song":[[6,4,1,"","added"],[6,4,1,"","album"],[6,4,1,"","album_id"],[6,4,1,"","artist"],[6,4,1,"","artist_id"],[6,4,1,"","available"],[6,4,1,"","bitrate"],[6,4,1,"","broken"],[6,2,1,"","by_filename"],[6,4,1,"","checksum"],[6,4,1,"","coverart"],[6,4,1,"","dirty"],[6,4,1,"","downloaded"],[6,4,1,"","duration"],[6,4,1,"","filesize"],[6,4,1,"","id"],[6,4,1,"","lastScanned"],[6,4,1,"","lastfm_mbid"],[6,4,1,"","lastfm_url"],[6,4,1,"","localpath"],[6,4,1,"","lyrics"],[6,2,1,"","random"],[6,4,1,"","tags"],[6,4,1,"","title"],[6,4,1,"","track_no"],[6,2,1,"","update_metadata"],[6,4,1,"","year"]],"wickedjukebox.model.db.library.SongHasGenre":[[6,4,1,"","genre"],[6,4,1,"","genre_id"],[6,4,1,"","id"],[6,4,1,"","song"],[6,4,1,"","song_id"]],"wickedjukebox.model.db.library.SongHasTag":[[6,4,1,"","id"],[6,4,1,"","song_id"],[6,4,1,"","tag_id"]],"wickedjukebox.model.db.library.StandingEnum":[[6,4,1,"","HATE"],[6,4,1,"","LOVE"]],"wickedjukebox.model.db.library.Tag":[[6,4,1,"","id"],[6,4,1,"","inserted"],[6,4,1,"","label"],[6,4,1,"","modified"]],"wickedjukebox.model.db.library.UserSongStanding":[[6,4,1,"","id"],[6,4,1,"","inserted"],[6,4,1,"","song_id"],[6,4,1,"","standing"],[6,4,1,"","user_id"]],"wickedjukebox.model.db.playback":[[6,1,1,"","Channel"],[6,1,1,"","DynamicPlaylist"],[6,1,1,"","QueueItem"],[6,1,1,"","RandomSongsToUse"],[6,1,1,"","State"]],"wickedjukebox.model.db.playback.Channel":[[6,4,1,"","active"],[6,4,1,"","backend"],[6,4,1,"","backend_params"],[6,4,1,"","id"],[6,4,1,"","name"],[6,4,1,"","ping"],[6,4,1,"","public"],[6,4,1,"","status"]],"wickedjukebox.model.db.playback.DynamicPlaylist":[[6,4,1,"","channel_id"],[6,4,1,"","group_id"],[6,4,1,"","id"],[6,4,1,"","label"],[6,4,1,"","probability"],[6,4,1,"","query"]],"wickedjukebox.model.db.playback.QueueItem":[[6,4,1,"","added"],[6,2,1,"","advance"],[6,4,1,"","channel"],[6,4,1,"","channel_id"],[6,4,1,"","id"],[6,2,1,"","next"],[6,4,1,"","position"],[6,4,1,"","song"],[6,4,1,"","song_id"],[6,4,1,"","user"],[6,4,1,"","user_id"]],"wickedjukebox.model.db.playback.RandomSongsToUse":[[6,4,1,"","id"],[6,4,1,"","in_string"],[6,4,1,"","used"]],"wickedjukebox.model.db.playback.State":[[6,4,1,"","channel_id"],[6,2,1,"","get"],[6,4,1,"","id"],[6,2,1,"","set"],[6,4,1,"","state"],[6,4,1,"","value"]],"wickedjukebox.model.db.sameta":[[6,3,1,"","connect"]],"wickedjukebox.model.db.settings":[[6,1,1,"","Setting"],[6,1,1,"","SettingText"]],"wickedjukebox.model.db.settings.Setting":[[6,4,1,"","channel_id"],[6,4,1,"","id"],[6,4,1,"","user_id"],[6,4,1,"","value"],[6,4,1,"","var"]],"wickedjukebox.model.db.settings.SettingText":[[6,4,1,"","text_en"],[6,4,1,"","var"]],"wickedjukebox.model.db.stats":[[6,1,1,"","ChannelAlbumDatum"],[6,1,1,"","ChannelStat"],[6,1,1,"","UserSongStat"]],"wickedjukebox.model.db.stats.ChannelAlbumDatum":[[6,4,1,"","album_id"],[6,4,1,"","channel_id"],[6,4,1,"","id"],[6,4,1,"","played"]],"wickedjukebox.model.db.stats.ChannelStat":[[6,4,1,"","channel"],[6,4,1,"","channel_id"],[6,4,1,"","cost"],[6,4,1,"","id"],[6,4,1,"","lastPlayed"],[6,2,1,"","last_played_parametric"],[6,4,1,"","played"],[6,4,1,"","skipped"],[6,4,1,"","song"],[6,4,1,"","song_id"],[6,4,1,"","voted"]],"wickedjukebox.model.db.stats.UserSongStat":[[6,4,1,"","song"],[6,4,1,"","song_id"],[6,4,1,"","user"],[6,4,1,"","user_id"],[6,4,1,"","when"]],"wickedjukebox.model.db.webui":[[6,1,1,"","DjangoAdminLog"],[6,1,1,"","DjangoCeleryResultsChordcounter"],[6,1,1,"","DjangoCeleryResultsGroupresult"],[6,1,1,"","DjangoCeleryResultsTaskresult"],[6,1,1,"","DjangoContentType"],[6,1,1,"","DjangoMigration"],[6,1,1,"","DjangoSession"],[6,1,1,"","ImageEnum"],[6,1,1,"","RenderPreset"],[6,1,1,"","RestFrameworkTrackingApirequestlog"],[6,1,1,"","Shoutbox"],[6,1,1,"","ThumbnailKvstore"]],"wickedjukebox.model.db.webui.DjangoAdminLog":[[6,4,1,"","action_flag"],[6,4,1,"","action_time"],[6,4,1,"","change_message"],[6,4,1,"","content_type"],[6,4,1,"","content_type_id"],[6,4,1,"","id"],[6,4,1,"","object_id"],[6,4,1,"","object_repr"],[6,4,1,"","user"],[6,4,1,"","user_id"]],"wickedjukebox.model.db.webui.DjangoCeleryResultsChordcounter":[[6,4,1,"","count"],[6,4,1,"","group_id"],[6,4,1,"","id"],[6,4,1,"","sub_tasks"]],"wickedjukebox.model.db.webui.DjangoCeleryResultsGroupresult":[[6,4,1,"","content_encoding"],[6,4,1,"","content_type"],[6,4,1,"","date_created"],[6,4,1,"","date_done"],[6,4,1,"","group_id"],[6,4,1,"","id"],[6,4,1,"","result"]],"wickedjukebox.model.db.webui.DjangoCeleryResultsTaskresult":[[6,4,1,"","content_encoding"],[6,4,1,"","content_type"],[6,4,1,"","date_created"],[6,4,1,"","date_done"],[6,4,1,"","id"],[6,4,1,"","meta"],[6,4,1,"","result"],[6,4,1,"","status"],[6,4,1,"","task_args"],[6,4,1,"","task_id"],[6,4,1,"","task_kwargs"],[6,4,1,"","task_name"],[6,4,1,"","traceback"],[6,4,1,"","worker"]],"wickedjukebox.model.db.webui.DjangoContentType":[[6,4,1,"","app_label"],[6,4,1,"","id"],[6,4,1,"","model"]],"wickedjukebox.model.db.webui.DjangoMigration":[[6,4,1,"","app"],[6,4,1,"","applied"],[6,4,1,"","id"],[6,4,1,"","name"]],"wickedjukebox.model.db.webui.DjangoSession":[[6,4,1,"","expire_date"],[6,4,1,"","session_data"],[6,4,1,"","session_key"]],"wickedjukebox.model.db.webui.ImageEnum":[[6,4,1,"","GIF"],[6,4,1,"","JPEG"],[6,4,1,"","PNG"]],"wickedjukebox.model.db.webui.RenderPreset":[[6,4,1,"","category"],[6,4,1,"","crop"],[6,4,1,"","description"],[6,4,1,"","force_mime"],[6,4,1,"","hmax"],[6,4,1,"","id"],[6,4,1,"","noproportion"],[6,4,1,"","placeholder"],[6,4,1,"","placeholder_image"],[6,4,1,"","preset"],[6,4,1,"","wmax"]],"wickedjukebox.model.db.webui.RestFrameworkTrackingApirequestlog":[[6,4,1,"","data"],[6,4,1,"","errors"],[6,4,1,"","host"],[6,4,1,"","id"],[6,4,1,"","method"],[6,4,1,"","path"],[6,4,1,"","query_params"],[6,4,1,"","remote_addr"],[6,4,1,"","requested_at"],[6,4,1,"","response"],[6,4,1,"","response_ms"],[6,4,1,"","status_code"],[6,4,1,"","user"],[6,4,1,"","user_id"],[6,4,1,"","username_persistent"],[6,4,1,"","view"],[6,4,1,"","view_method"]],"wickedjukebox.model.db.webui.Shoutbox":[[6,4,1,"","added"],[6,4,1,"","id"],[6,4,1,"","message"],[6,4,1,"","user"],[6,4,1,"","user_id"]],"wickedjukebox.model.db.webui.ThumbnailKvstore":[[6,4,1,"","key"],[6,4,1,"","value"]],"wickedjukebox.scanner":[[1,3,1,"","collect_files"],[1,3,1,"","is_valid_audio_file"],[1,3,1,"","process"],[1,3,1,"","process_files"],[1,3,1,"","scan"]],"wickedjukebox.smartplaylist":[[7,0,0,"-","dbbridge"],[7,0,0,"-","parser"]],"wickedjukebox.smartplaylist.dbbridge":[[7,3,1,"","parse_dynamic_playlists"]],"wickedjukebox.smartplaylist.parser":[[7,6,1,"","ParserSyntaxError"],[7,3,1,"","get_tokens"],[7,3,1,"","p_error"],[7,3,1,"","p_expression"],[7,3,1,"","p_statement"],[7,3,1,"","parse_query"],[7,3,1,"","t_ID"],[7,3,1,"","t_error"],[7,3,1,"","t_value"]],wickedjukebox:[[1,0,0,"-","channel"],[2,0,0,"-","cli"],[3,0,0,"-","component"],[1,0,0,"-","config"],[4,0,0,"-","core"],[1,0,0,"-","exc"],[1,0,0,"-","logutil"],[5,0,0,"-","model"],[1,0,0,"-","scanner"],[7,0,0,"-","smartplaylist"]]},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","method","Python method"],"3":["py","function","Python function"],"4":["py","attribute","Python attribute"],"5":["py","property","Python property"],"6":["py","exception","Python exception"],"7":["py","data","Python data"]},objtypes:{"0":"py:module","1":"py:class","2":"py:method","3":"py:function","4":"py:attribute","5":"py:property","6":"py:exception","7":"py:data"},terms:{"0":[1,3,6,8,9,16],"1":[3,9,13,16],"10":[3,6,9,13,15],"1000":8,"120":[3,9,13],"1209600":4,"127":[3,9,16],"14":8,"3":8,"4":[3,9,13],"450":9,"5":1,"600":[3,13],"604800":4,"6600":[3,8,9,16],"8":[1,5,8],"abstract":[1,3,5],"case":3,"class":[1,3,4,5,6,13,14,15,16,17],"default":[1,3,6,8,11,12,14,17],"enum":[1,3,4,6],"float":4,"function":[1,3,7],"import":[3,9,13],"int":[1,2,3,4,5],"long":[3,13],"new":[3,9,18],"null":[3,9,13,14,15,16,17],"public":6,"return":[1,3,4,6,13,17],"static":[1,5,6],"true":[1,3,8],"var":[6,8,9],"while":4,A:[1,3,4,14,15,16,17],AND:7,As:[3,13],At:[9,12],For:[1,6,9,11,12,18],If:[1,3,9,12,14,16],In:12,It:[3,8,13,15,18],No:[3,13],OR:7,On:11,Or:11,The:[1,3,4,6,9,12,13,18],Then:1,There:[3,13],To:12,__repr__:1,_io:[1,5],_t:[1,3],abc:3,abl:8,absolut:6,abstractipc:[1,3],abstractjingl:[1,3],abstractplay:[1,3],abstractqueu:[1,3],abstractrandom:[1,3],access:[5,10],accord:[3,13],account:4,action:[3,14],action_flag:6,action_tim:6,activ:[3,6,13],actual:9,ad:[3,4,6,18],add:[1,3,8,9,13],addgroup:8,addit:[3,13],addus:8,admin:[6,10,12],advanc:6,affect:[3,13],after:[3,4,15,18],ag:4,again:3,ahead:[3,13],albert:8,album:6,album_id:6,alchemi:6,alemb:12,alia:3,all:[3,5,12,13],allfiles_random:[3,13],allfilesrandom:[3,13],allow:[1,3,12,14],alpin:8,alreadi:12,also:5,alwai:[3,13,17],amount:[3,13],an:[1,3,4,5,6,7,12,13,14,15,17],ani:[1,3,4,9,12],anyth:9,api:10,apk:8,app:[2,6],app_label:6,append:3,appli:[6,12],applic:[1,3,6,9,12,14],appropri:[1,12],ar:[1,3,4,8,12,13,14,18],arg:[2,3,6],argpars:2,argument:[2,3,14,18],argv:5,around:1,arriv:3,artist:6,artist_id:6,aspect:9,assum:8,audibl:12,audio:[1,8],audio_output:8,audiometa:[0,1],auth:[1,5],authent:6,authgroup:6,authgrouppermiss:6,authoris:6,authpermiss:6,authus:6,authusergroup:6,authuseruserpermiss:6,auto:12,autom:12,autoplai:[1,3,9],autospawn:8,avail:[3,6,11,18],back:[3,9,17],backend:[3,6,9,11,14,16],backend_param:6,background:[3,12],base:[1,3,4,5,6,7,12,13,15,17],becom:[3,12],been:[3,4,8,11,13],befor:[1,12],behaviour:[3,9,14],best:4,bin:[8,12,18],binari:[8,18],bind:6,bind_to_address:8,bio:6,bitrat:6,bonu:4,bool:[1,3,4],boost:4,bootstrap:2,both:[12,18],bound:[3,6,13],bridg:[3,16],bring:12,broken:[1,6],build:[3,11,13,15],by_filenam:6,by_nam:6,c:18,cach:8,calcul:[3,4,13],call:[1,3,9,14,16],callabl:[1,3],caller_sourc:1,can:[1,3,5,8,11,12,13,14],cannot:1,cap:4,categori:6,caus:5,certain:[3,9,14],cfg:[3,9],chang:[3,12],change_messag:6,channel:[0,2,3,4,6,9,10,12,13,14,15,16,17],channel_id:6,channel_nam:[2,3,6,13,14,15,16,17],channelalbumdatum:6,channelstat:6,charset:9,check:1,checker:3,checksum:6,chown:8,cl:1,clarifi:4,classmethod:6,claus:7,cli:[0,1],client:8,close:12,clsmap:3,code:[1,4],codenam:6,collect:6,collect_fil:1,collection_id:6,collectionhassong:6,column:4,come:1,command:[2,3,12,14,18],commun:9,complet:9,compon:[0,1,9,12,13,14,15,16,17],compos:9,conceptu:9,concurr:3,conf:8,config:[0,3,8,12,13,14,15,16,17,18],config_kei:3,configerror:1,configkei:[1,3],configopt:1,configpars:1,configscop:1,configur:[1,3,4,10,13,14,15,16,17,18],connect:[3,6,8,9,11,12,13],consid:[3,4,11,13],construcst:7,constructor:3,contain:[1,3,4,6,7,8,9,12,13,14,15,16,17],content:[0,12,14],content_encod:6,content_typ:6,content_type_id:6,continu:[1,12],control:11,conveni:[8,12],convert:[1,3,7],cooki:6,copi:8,core:[0,1,3,6,10],cost:6,count:6,countri:6,country_cod:6,country_nam:6,coverart:6,creat:[3,5,12,14],credit:6,crop:6,curl:8,current:[3,13,14,18],currentl:3,d:8,daemon:[3,8,16],dash:4,data:[3,5,6,7,18],databas:[1,3,4,6,7,9,10,13,14,17,18],databasequeu:[3,17],date:[4,6],date_cr:6,date_don:6,date_join:6,db:[1,3,4,5,9,12,13,14,17],db_file:8,db_port:9,dbbridg:[0,1],dbipc:[3,14],debug:7,decl_api:6,decode_text:5,default_config:1,defin:[1,3,4,13,14],definit:6,depend:[3,5,12,18],dequeu:3,descript:6,detail:9,detectd:1,determin:4,develop:10,dict:[3,5],dictifi:1,dictionari:[1,5],diff:12,differ:[1,3,9,12,16],digest:4,directli:11,directori:1,dirti:6,disabl:[8,9],disk:[3,6,14],displai:5,display_fil:5,distribut:11,divid:4,django_user_id:6,djangoadminlog:6,djangoceleryresultschordcount:6,djangoceleryresultsgroupresult:6,djangoceleryresultstaskresult:6,djangocontenttyp:6,djangomigr:6,djangosess:6,docker:[9,10,11,12],dockerfil:8,document:9,doe:[3,16],don:4,done:12,download:6,downstream:[3,13],dsn:[1,6,9],dummi:[3,13],durat:[4,6],dure:[1,12],dynam:7,dynamicplaylist:6,each:[1,3,9,14],edit:12,editor:12,either:[4,11],email:6,empti:[3,6,13,14,17],enabl:8,encod:[1,5,6],end:[3,6,9],enddat:6,enqueu:3,ensur:3,entri:[2,4],entrypoint:8,enumer:6,env:[8,12,18],environ:[10,11,18],equal:7,error:[1,3,6,13],establish:6,etc:8,event:[1,5],everyth:[1,8],ex:[5,9],exact:[3,13],exactli:1,exampl:[1,3,8,10,12,13,14,15,16,17],exc:0,except:[1,3,7],exclud:3,exec:12,execut:[3,5,13,14],exist:[3,12],expect:1,expens:3,expire_d:6,expos:[5,8],express:[4,7],extern:[3,5,14],f:[5,9],fab:12,fabfil:12,fabric:12,fact:[3,15],factori:5,fallback:1,fals:[3,8],far:11,fetch:[3,4],field:[3,5,7],file:[1,3,5,6,8,9,10,11,13,14,15,16,18],filebasedjingl:[3,15],filenam:[1,3,5,6,13,17],files:6,filesystem_charset:8,filetyp:[5,9],filter:7,find:[1,4],find_song:4,first_nam:6,flac:5,folder:[1,3,8,12,14,16,18],follow:[11,12,18],force_mim:6,found:[1,6],frame:1,from:[1,3,4,6,7,8,9,11,12,13,15,17],frontend:9,fs:[3,9,14,15],fsipc:[3,14],fsstatefil:3,full:3,fullnam:6,gain:4,gather:6,gener:[1,4,7,12],genr:6,genre_id:6,get:[1,3,4,6],get_album:5,get_artist:5,get_autoplai:3,get_bitr:5,get_com:5,get_dur:5,get_genr:5,get_ipc:3,get_jingl:3,get_play:3,get_queu:3,get_release_d:5,get_sect:1,get_standing_queri:4,get_titl:5,get_token:7,get_total_track:5,get_track_no:5,gif:6,git:11,given:[1,3,4,13,14],global:1,got:3,group:6,group_id:6,ha:[1,3,8,9,11,16],hand:12,handi:1,handl:[3,5,12,15],har:[3,13],hate:[4,6],have:[3,4,13],head:12,header:1,help:18,helper:[1,2,7],here:8,higher:[3,13],histori:6,hmax:6,home:8,host:[3,6,8,9,12,16],how:[1,3,13],http:11,i:4,id:[4,6],ident:5,imag:[6,8],imageenum:6,immedi:3,impact:[3,9,13],implement:[3,9,13,14,15,16,17],in_str:6,inact:[3,13],inconsist:5,independ:9,index:10,indic:3,influenc:4,info:1,inform:[1,5,18],ini:[1,12],inject:8,input:[7,8],insert:[6,12,18],insid:[9,10,11,12],instal:[8,10,18],instanc:[1,3,5,10],instanti:3,intend:[3,13],inter:[3,9,14],interact:6,interfac:[2,3,5],intern:[3,5],interpret:3,interv:[3,9,15],invalid:3,invalidcommand:3,invok:3,ip:6,ipc:[0,1,9],is_act:6,is_empti:3,is_jingl:3,is_mysql:4,is_plai:3,is_staff:6,is_superus:6,is_valid_audio_fil:1,item:5,its:[4,11],jingl:[0,1,9],jpeg:6,jukebox2mpd:3,jukebox:[1,3,8,9,10,12,14,16],jukebox_admin:[0,1],jukebox_path:[3,9],jukeboxdb:12,jukeox:9,keep:6,kei:[1,3,5,6],keyword:3,known:3,kontext:1,kwarg:[3,6],label:6,lambda:1,last:4,last_login:6,last_nam:6,last_plai:[4,6],last_played_cutoff:4,last_played_parametr:6,lastfm:[1,5],lastfm_mbid:6,lastfm_url:6,lastfmqueu:6,lastplai:6,lastscan:6,lat:6,latest:12,layer:5,lead:[3,13],least:9,left:12,level:1,lib:[8,9],librari:[1,4,5,9],lifetim:6,like:[1,3,7,12,13,14],line:[1,2,18],link:1,linux:11,list:[1,5],listen:[3,4,13],load:[1,6],load_config:1,local:[3,6,8,16,18],localhost:12,localpath:[4,6],locat:[1,12],log:[1,3,5,8,14,15,16,17],log_fil:8,logger:3,logutil:0,lon:6,longer:[3,4,13],lookup:1,love:[4,6],lp_cutoff:[4,6],lparen:7,lu:8,lyric:6,m:12,mai:[3,13],main:[1,2,5,12,18],maintain:8,mainten:10,make:[3,12,13],make_channel:2,make_component_gett:3,mandatori:18,mani:[3,4,15],map:[3,4,12,18],max_dur:[3,4,9,13],max_random_dur:4,maximum:4,mechan:9,memori:8,messag:[6,12],meta:[1,5,6,18],metadata:[1,5,6,12],metafactori:5,method:[3,6,7],mex:4,michel:8,migrat:12,mode:[1,5,9,18],model:[0,1,4,9,12],modif:12,modifi:[4,6,10],modul:[0,10],modular:[3,9],more:[1,3,13,18],most:[3,9,12,13],mount:8,mp3:[3,5,8,9,12,16,18],mp3meta:5,mpd2jukebox:3,mpd:[3,9,10,11,16],mpd_path:[3,9],mpdplayer:[3,12,16],mpduser:8,multipli:4,music:[3,6,8,9,10,11,13,18],music_directori:8,must:[3,12],mutagen:5,mutagen_meta:5,my_inner_funct:1,myfunct:1,mysql:[9,12],name:[1,3,5,6,8,9,13,14,15,18],namedtupl:[1,3],namespac:2,nativ:8,ncmpcpp:8,necessari:[5,12,18],need:[1,3,4,8],neg:[3,13],never:[3,4,13],never_plai:4,next:[3,4,6,13,15],nocredit:6,none:[1,3,6,7],noproport:6,note:4,noth:[3,9,16],nullipc:[1,3,14],nulljingl:[1,3,15],nullplay:[1,3,16],nullqueu:[1,3,17],nullrandom:[3,13],num_active_us:4,number:[3,4],o:8,object:[1,3,5],object_id:6,object_repr:6,off:[3,13],offlin:[3,13],old:4,one:[3,6,13,15,18],onli:[3,4,9,11,13,16,17,18],onto:[1,3],op:[3,13,14,15],open:[11,12],oper:[3,17],option:[1,2,3,4,6,9,13,14,15,16,17],order:12,origin:[1,5],orm:[4,6],other:[3,14],outsid:3,over:18,overal:4,overrid:[3,5],overwritten:12,p:[7,8,12],p_error:7,p_express:7,p_statement:7,packag:[0,10,18],page:10,param:6,paramet:[1,3,4,6],parent:1,pars:2,parse_arg:2,parse_dynamic_playlist:7,parse_queri:7,parser:[0,1],parsersyntaxerror:7,part:[1,9],pass:3,password:[6,8,12],path:[1,3,6,8,9,11,12,13,14,15,16,18],path_map:[3,9,16],pathlib:[1,3],pathmap:3,peopl:6,permiss:6,permission_id:6,persist:[3,13],photo:6,pick:[3,9,13,15],pictur:6,pid:8,pid_fil:8,ping:6,pinnedip:6,pip:11,placehold:6,placeholder_imag:6,plai:[3,4,6,9,11,13,15],plain:[3,14],playback:[1,5],player:[0,1,9,12],playlist:[3,6,7,8,11],playlist_directori:8,playlist_id:6,playlisthassong:6,plugin:8,png:6,point:[1,2,4],pop:12,port:[3,9,16],posit:[3,6,13],possibl:[1,3,4,8,13,15],prefetch:[3,13],preset:6,prevent:8,primaci:4,primarili:[3,6,13],probabl:6,procedur:18,process:[1,3,8,9,11,12,14,18],process_fil:1,process_rescan:2,produc:9,progress:1,project:12,proof_of_lif:[4,6],proof_of_life_timeout:4,proof_of_listen:6,proofoflife_timeout:[3,4,9,13],proper:5,properti:3,provid:[1,3,5,18],pth:1,puls:8,pulseaudio:8,pymysql:9,python:[1,11],qualifi:1,qualnam:1,qualname_repr:1,queri:[3,4,6,7,13],query_param:6,queu:[3,9,17],queue:[0,1,6,9,13],queue_add:6,queue_id:6,queue_remov:6,queue_skip:6,queueitem:6,r:8,rais:[1,3],random:[0,1,4,6,13,15],randomsongstous:6,readili:3,real:6,receiv:4,recenc:4,recent:[3,4,13],recov:12,recurs:[3,13,15,18],rel:[3,4],relat:[4,6],release_d:6,reli:[3,14],remaining_second:3,rememb:4,remote_addr:6,remov:3,renderpreset:6,repositori:11,repres:[3,14],requested_at:6,requir:[3,8,10,12,14,18],rescan:[12,18],resourc:8,respect:3,respons:[6,9],response_m:6,restframeworktrackingapirequestlog:6,result:[1,3,6,13],resum:3,retriev:[1,4,6,7],return_typ:3,review:12,revis:12,right:12,rm:8,ro:8,root:[1,3,9,13,15,16],rparen:7,run:[1,2,3,4,8,9,10,11,14,16],run_channel:[0,1],s:[3,8],same:5,sameta:[1,5],save:[6,12],scan:[1,6,10,18],scanner:0,schema:[3,10,14,17],scope:1,score:[3,4,13],score_express:4,scoring_config:[3,4],scoringconfig:[3,4],script:12,search:10,second:[3,4,13],section:[1,3,9,18],see:[9,12],select:[6,9],semant:1,sens:[3,13],sentinel:1,separ:8,sequenti:3,server:8,session:[4,6],session_data:6,session_kei:6,set:[1,3,5,8,9,10,18],setcap:8,setting_nam:4,settingtext:6,setup_log:1,share:8,shm:8,should:[3,12],shoutbox:6,side:12,simpl:[1,3,13,14],simpli:[3,14,15],simplifi:7,sinc:[3,4,13],singl:[3,14],skip:[3,6,14],skip_request:3,slightli:1,smart:[3,4,7],smart_prefetch:[3,9,13],smart_random_no_us:4,smart_random_with_us:4,smartfind:[0,1,3],smartplaylist:[0,1],smartprefetch:[3,13],smartprefetchthread:3,so:[3,11,12,13],socket:8,solut:[3,14],some:1,someth:[1,9],song:[3,4,6,9,13,14,15],song_ag:4,song_age_cutoff:4,song_id:6,songhasgenr:6,songhastag:6,soon:3,sound:9,sourc:[1,4],space:8,specif:[3,5,6],split:9,sql:[6,7,8],sqlalchemi:[4,6],stack:1,stand:[4,6],standard:3,standardis:5,standingenum:6,start:[3,6,11,12],startdat:6,startup:11,stat:[1,5],state:[3,6,8,13,14],state_fil:8,statement:7,statenam:6,statist:[3,4,6],statu:6,status_cod:6,stdout:[1,5,8],steer:6,sticker:8,sticker_fil:8,storag:[3,17],store:[1,5],str:[1,2,3,4,5,6,7,13,14,15,16,17],stream:[1,5],string:[7,9,12],sub:[6,18],sub_task:6,subclass:3,submodul:0,subpackag:0,subsect:1,subsequ:12,successfulli:3,sum:[3,13],summari:6,support:9,system:[3,6,9,17,18],t:[4,7],t_error:7,t_id:7,t_valu:7,tabl:[3,6,14,17],tag:[6,8],tag_cach:8,tag_id:6,take:[3,4,13],taken:[3,4,14],target:[3,12],task:12,task_arg:6,task_id:6,task_kwarg:6,task_nam:6,tcp:11,templat:12,temporari:12,test:[1,3,10,11,13],text:[3,14],text_en:6,textio:[1,5],textiowrapp:[1,5],tfallback:1,than:[3,4,13,16],thei:[1,4],thi:[1,3,4,5,6,7,9,12,13,14,15,16,17,18],those:[3,13],thread:3,thumbnailkvstor:6,ti:12,tick:1,tick_interval_:1,time:[3,4,9,12,13],time_plai:6,time_start:6,titl:[5,6],todo:4,token:7,tool:18,touch:[3,14],traceback:6,track_no:6,translat:[3,16],tree:[3,13,15],trigger:[3,14],tupl:4,two:[9,12,18],type:[1,3,6,8,9,13,14,15,16,17],u:12,ui:6,uid:8,unam:8,und:3,underli:[3,9,14,16],union:1,unix:8,unset:1,until:3,up:[8,10,18],updat:18,update_metadata:6,upgrad:12,upper:[3,13],us:[3,5,6,7,8,9,11,12,13,14,16,17,18],usag:10,user:[3,4,6,8,13,17,18],user_id:6,user_r:4,usernam:6,username_persist:6,usersongstand:6,usersongstat:6,usr:[8,18],utf8:9,utf:[1,5,8],util:8,v:18,valid:1,valu:[1,3,4,5,6,7,13,14],variabl:[1,3,6,13],verbos:1,veri:[3,12,13],version:12,via:[3,8,9],view:6,view_method:6,vim:9,virtual:[11,12,18],volum:8,vote:6,w:[1,5,7],wai:5,wait:3,walk:18,warn:3,we:[1,3,15],web:6,websit:6,webui:[1,5],weigh:[3,13],weight:[3,4,6,13],weight_:[3,13],weight_last_plai:[3,9,13],weight_never_plai:[3,9,13],weight_random:[3,9,13],weight_song_ag:[3,9,13],weight_user_r:[3,9,13],well:[1,3,13],were:4,when:[3,4,6,9,12,18],where:[1,3,7,14],whether:[3,4],which:[1,3,9,13,16,17],whl:11,whole:9,wick:[8,9,12],wickedjukebox:[8,9,11,12,13,14,15,16,17],wickedjukebox_mpd:8,wickedjukeboxexcept:1,wide:18,wikipag:6,within:4,without:[4,9],wmax:6,work:12,worker:6,workflow:12,world:[3,6],would:[3,4,15],wrap:5,write:[1,9,12],xe:8,year:6,yet:[3,12],you:[3,8,11],your:[11,18]},titles:["wickedjukebox","wickedjukebox package","wickedjukebox.cli package","wickedjukebox.component package","wickedjukebox.core package","wickedjukebox.model package","wickedjukebox.model.db package","wickedjukebox.smartplaylist package","MPD Inside Docker","Configuration","Welcome to wickedjukebox\u2019s documentation!","Installation","Maintenance","Autoplay Modules","IPC Modules","Jingle Modules","Player Modules","Queue Modules","Usage"],titleterms:{access:12,admin:18,appendix:10,audiometa:5,auth:6,autoplai:13,channel:[1,18],cli:2,compon:3,config:1,configur:9,content:[1,2,3,4,5,6,7,10],core:[4,9],databas:12,db:6,dbbridg:7,develop:12,docker:8,document:10,environ:12,event:6,exampl:[9,18],exc:1,execut:18,file:12,indic:10,insid:8,instal:11,instanc:12,ipc:[3,14],jingl:[3,15],jukebox:18,jukebox_admin:2,lastfm:6,librari:6,log:6,logutil:1,mainten:12,model:[5,6],modifi:12,modul:[1,2,3,4,5,6,7,9,13,14,15,16,17],mpd:[8,12],music:12,packag:[1,2,3,4,5,6,7,11],parser:7,playback:6,player:[3,16],queue:[3,17],random:3,requir:11,run:[12,18],run_channel:2,s:10,sameta:6,scan:12,scanner:1,schema:12,set:[6,12],smartfind:4,smartplaylist:7,stat:6,submodul:[1,2,3,4,5,6,7],subpackag:[1,5],tabl:10,test:12,up:12,usag:18,webui:6,welcom:10,wickedjukebox:[0,1,2,3,4,5,6,7,10]}})