          <h1>My Jukebox</h1>
          <p>logged in as <b>{$USERINFO.fullname}</b></p>
          <p>
          <b>Group:</b> {$PERMISSIONS.title}<br />
          <b>Credits:</b> {$USERINFO.credits}<br />
          <b>Songs queued:</b> {$USERINFO.selects}<br />
          <b>Downloads:</b> {$USERINFO.downloads}<br />
          <b>Songs Skipped:</b> {$USERINFO.skips}<br />
          </p>
          <p><a href="#" onclick="javascript:logout();">logout</a></p>
