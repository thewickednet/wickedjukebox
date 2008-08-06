<h1>Quick search</h1>

            <form name="qsearch" id="qsearch" onsubmit="return quicksearch();">
            <img src="/images/carousel.gif" align="right" style="display:none;" id="qsearch_carousel" align="right" />
            <input type="text" maxlength="255" name="body" /><input type="submit" name="submit" value="find!" class="button" />
            <input type="hidden" name="module" value="splash" />
            <input type="hidden" name="action" value="search" />
            </form>
            <div id="qresults">
            <p>enter a keyword to do a quick search on songs!</p>
            <p>only 15 results will be returned, be as precise as possible.</p>
            </div>
