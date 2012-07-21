//code by badblood.twn 2012_07_07_2303


package dan.test.a;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.URLEncoder;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.NameValuePair;
import org.apache.http.auth.UsernamePasswordCredentials;
import org.apache.http.client.HttpClient;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.impl.auth.BasicScheme;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.message.BasicNameValuePair;
import org.json.JSONArray;
import org.json.JSONObject;


public class WickedjukeboxRestClient 
{
    private JSONArray jsonArray;
    private JSONObject jsonObject;
    private String userName;
    private String password;
    private HashMap<String, String> queryMap;
    
    //url definition
    private String currentSong;

    
    
    public WickedjukeboxRestClient(String user, String pass)
    {
    	currentSong = "https://wickedjukebox.com/rest/channel/";
    	userName = user;
    	password = pass;
    	queryMap = new HashMap<String, String>();
    }
    
    
    /**
     * get current song
     */
    public String getCurrentSong()
    {
        
    	String temp;
    	temp = null;
        try
        {
        
            HttpClient httpClient = new DefaultHttpClient();
            HttpGet httpGet = new HttpGet(currentSong);
            httpGet.addHeader(BasicScheme.authenticate(
            					new UsernamePasswordCredentials(userName, password), "UTF-8", false));



            HttpResponse httpResponse = httpClient.execute(httpGet);
            HttpEntity responseEntity = httpResponse.getEntity();

            // read the stream returned by responseEntity.getContent()
            
            BufferedReader buff = new BufferedReader(new InputStreamReader(responseEntity.getContent()));
            
            String outputStr = buff.readLine();
            
            ////System.out.println("aus der current song method: " + outputStr);
            
            //////////////////////////////////////////////////////////////////////////////////////////////
            //json
            
            //create json object of the outputStr
			//it works but sucks :(
            
			jsonObject = new JSONObject(outputStr);
			String test1 = jsonObject.toString();
			//System.out.println(test1);
			
			jsonArray = jsonObject.getJSONArray("payload");		
			
			//System.out.println(jsonArray.length());				
			
			JSONObject test2 = jsonArray.getJSONObject(1);		//get standard channel
			
			JSONObject test3 = test2.getJSONObject("current");	//get current JSONObject
			
			JSONObject test4 = test3.getJSONObject("song");		//get song JSONObject
			
			JSONObject test5 = test4.getJSONObject("artist");	//get artist JSONObject
			
			//System.out.println("test4 " + test4.names());		//list all names in song
			
			String tempArtist = test5.getString("name");
			
			temp = tempArtist + " - " + test4.getString("title"); //current title as String 
	
        }
        catch (Exception e)
        {
            //System.out.println("Uuups:" + e);
        }
        
        return temp;
    }

    
    /**
     * search query
     */
    public HashMap sendQuery(String query)
    {
    	String title = "";
    	String id = "";
    	JSONObject artist;
    	String artistStr = "";
    	
    	try
        {

    		String restUrl = URLEncoder.encode(query, "UTF-8");  //encode spaces and so on in url format
    		
    		HttpClient httpClient = new DefaultHttpClient();
            HttpGet httpGet = new HttpGet("https://wickedjukebox.com/rest/search/?q=" + restUrl);
            httpGet.addHeader(BasicScheme.authenticate(
					new UsernamePasswordCredentials(userName, password), "UTF-8", false));



            HttpResponse httpResponse = httpClient.execute(httpGet);
            HttpEntity responseEntity = httpResponse.getEntity();

            // read the stream returned by responseEntity.getContent()

            BufferedReader buff = new BufferedReader(new InputStreamReader(responseEntity.getContent()));

            String temp = buff.readLine();

            ////////////////////////////////////////////////////////////////////////////////////////////
            //json object from wickedjukebox contains two further json objects "ref" and "payload"
            JSONObject jsonObject = new JSONObject(temp);
            String test1 = jsonObject.toString();

            JSONArray payloadArray = jsonObject.optJSONArray("payload");

            //System.out.println("JSONArray length : " + payloadArray.length());


            //list all objects in payloadArray
            for (int i = 0; i < payloadArray.length(); i++)
            {
                JSONObject tempObj = payloadArray.optJSONObject(i);
                ////System.out.println("json object in payload : " + tempObj.toString());


                if (tempObj.has("title") && tempObj.has("id"))
                {
                    title = tempObj.getString("title");
                    id = tempObj.getString("id");
                }

                
                //String tempArtist = tempObj.getString("artist");
                //artist = new JSONObject(tempArtist);
                //artistStr = artist.getString("artist");


         //       System.out.println(artistStr + " -- " + title + " " + id);
                
                queryMap.put(id, title);

            }
            
            //System.out.println("Et sinn der fond ginn : " + queryMap.size());
        }
        catch (Exception e)
        {
            System.out.println(e);
        }
    	
    	return queryMap;
    }//end sendQuery


////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * add title to queue
     */
    
    public void queueTest(String id)
    {
	HttpClient client = new DefaultHttpClient();
	HttpPost post = new HttpPost("https://wickedjukebox.com/rest/queue/");
	try 
            {
                
                ////System.out.println("WebPost 1");
                
                post.addHeader(BasicScheme.authenticate(
                           new UsernamePasswordCredentials("badblood.twn", "woper78"), "UTF-8", false));
                
                //System.out.println("WebPost 2");
                
                List<NameValuePair> nameValuePairs = new ArrayList<NameValuePair>(1);
                nameValuePairs.add(new BasicNameValuePair("song_id", id));
                
                //System.out.println("WebPost 3");
                
                //System.out.println("ass nameValuePairs eidel? :" + nameValuePairs.isEmpty());
                
//                UrlEncodedFormEntity tempEntity = new UrlEncodedFormEntity(nameValuePairs, "utf-8");
//                
//                //System.out.println("hei kennt neischt :" + tempEntity.toString());
                
                
                
                post.setEntity(new UrlEncodedFormEntity(nameValuePairs, "UTF-8"));

                //System.out.println("WebPost 4");
                
                HttpResponse response = client.execute(post);
                
                //System.out.println("WebPost 5");
                
                BufferedReader rd = new BufferedReader(new InputStreamReader(response.getEntity().getContent()));
                String line = "";
            
                while ((line = rd.readLine()) != null) 
                {
                        //System.out.println(line);
                }

            } 
            catch (Exception e) 
            {
                //System.out.println("an der queueest method ass ee fehler : " + e);
            }
    }
    
}
	

