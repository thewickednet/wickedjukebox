<h1>Shoutbox</h1>

            <form name="shouter"  id="shouter" onsubmit="return shout();">
            <input type="text" maxlength="255" name="body" /><input type="submit" name="submit" value="shout!" class="button" />
            <input type="hidden" name="module" value="shoutbox" />
            <input type="hidden" name="action" value="shout" />
            </form>
            <div id="shoutboxmsgs">
            </div>

			<script>
			shoutbox();
			</script>
