
          <h1>My Jukebox</h1>
          <form name="loginform" onsubmit="return login();">
          {if $AUTH_ERROR ne ''}
          <img src="/images/exclamation.png" /> {$AUTH_ERROR}<br />
          {/if}
          <input type="text" name="username" value="{$AUTH_USER}" />
          <br />
          <input name="password" type="password" value="" />
          <input type="submit" value="Log In" />
          </form>
          <script>
          document.loginform.username.focus();
          </script>
