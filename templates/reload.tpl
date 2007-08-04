<p>&nbsp;</p>
<p>
{if $RELOAD_MESSAGE eq 'LOGOUT_SUCCESS'}
<img src="/images/tick.png" /> you have been logged out.
{else if $RELOAD_MESSAGE eq 'AUTH_SUCCESS'}
<img src="/images/tick.png" /> you have successfully logged in.
{/if}
</p>

<p>reloading page. please wait.</p>

<p><img src="/images/carousel.gif" /></p>

<script>

window.location.reload();

</script>