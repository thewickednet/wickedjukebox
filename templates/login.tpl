
          <h1>My Jukebox</h1>
          <form name="loginform" onsubmit="return login();">
          {$AUTH_ERROR}<br />
          <input type="text" name="username" value="{$AUTH_USER}" />
          <br />
          <input name="password" type="password" value="" />
          <input type="submit" value="Log In" />
          </form>
