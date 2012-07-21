//code by badblood.twn 2012_07_07_2303


package dan.test.a;

import java.util.HashMap;
import java.util.HashSet;
import android.app.Activity;
import android.os.Bundle;
import android.os.StrictMode;
import android.view.View;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.Toast;


public class GuiTestActivity extends Activity
{
    
	private Button searchButton;		//list button
	private EditText editText;
	private ListView listView;
	private Button currentSongButton;
	private WickedjukeboxRestClient wickedClient;
	private String[] idArray;
	private String[] titleArray;
	
	/** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState) 
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
        
        //ignore that all network operations should run in a different thread
        //problem appears by upgrading android 2.3.3 to Android >= 3
        if (android.os.Build.VERSION.SDK_INT > 9) {
            StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder().permitAll().build();
            StrictMode.setThreadPolicy(policy);
          }

        ////////////////////////////////////////////////////////////////////
        //list button code
    	searchButton = (Button)findViewById(R.id.button1);
    	currentSongButton = (Button)findViewById(R.id.buttonCurrentSong);
    	
    	
    	editText   = (EditText)findViewById(R.id.editText1);

        

        ////////////////////////////////////////////////////////////////////
        //BUTTONS definition
    	
        currentSongButton.setOnClickListener(
                new View.OnClickListener()
                {
                    public void onClick(View view)
                    {
                        //System.out.println("de current song knapp ass gedreckt ginn :)");
                        
                        wickedClient = new WickedjukeboxRestClient("badblood.twn", "woper78");
                        
                        //System.out.println("de current song ass " + wickedClient.getCurrentSong());
                         
                    	// When clicked, show a toast with the TextView text
                    	Toast.makeText(getApplicationContext(), wickedClient.getCurrentSong(), Toast.LENGTH_SHORT).show();
                    		    
                    }
               	});//end currentSonButton
                        

        searchButton.setOnClickListener(
                new View.OnClickListener()
                {
                    public void onClick(View view)
                    {
                        //System.out.println("de searchButton knapp ass gedreckt ginn :)");
                        
                        wickedClient = new WickedjukeboxRestClient("badblood.twn", "woper78");
                        
                        String searchTitle = editText.getText().toString();	//get search query from text label
                        
                        
                        HashMap tempMap = wickedClient.sendQuery(searchTitle);
                        
                        //System.out.println("map huet :" + tempMap.size());
                        
                        HashSet<String> keySet = new HashSet<String>(tempMap.keySet());
                        
                        
                        idArray = new String[tempMap.size()];
                        titleArray = new String[tempMap.size()];
                        
                        int index = 0;
                        
                        for (String eachStr : keySet)
                        {
                        	//System.out.println(eachStr + " " + tempMap.get(eachStr));
                        	
                        	idArray[index] = eachStr;
                        	titleArray[index] = (String) tempMap.get(eachStr);
                        	index++;
                        	
                        }
                        
                        //System.out.println("set " + keySet.size());
                        
                    	// When clicked, show a toast with the TextView text
                    	Toast.makeText(getApplicationContext(), "Sichen ...", Toast.LENGTH_SHORT).show();
                    	
                    	
                    	for (int i = 0 ; i < titleArray.length; i++)
                    	{
                    		//System.out.println("den titleArray : " + titleArray[i]);
                    		
                    	}
                    	
                    	                    	
                    	listViewQueryResults(titleArray);	//populate list with titleArray	    
                    }
               	});
        
        
    }//end onCreate

   
    
    public void listViewQueryResults(String[] tempResults)
    {
    	listView = (ListView) findViewById(R.id.mylist);
    	
    	// First paramenter - Context
    	// Second parameter - Layout for the row
    	// Third parameter - ID of the View to which the data is written
    	// Forth - the Array of data
    	ArrayAdapter<String> adapter = new ArrayAdapter<String>(this,
    		android.R.layout.simple_list_item_1, android.R.id.text1, tempResults);

    	// Assign adapter to ListView
    	listView.setAdapter(adapter);
    	
        listView.setOnItemClickListener(new OnItemClickListener() 
        { 
	        public void onItemClick(AdapterView<?> parent, View v, int position, long id) 
	        { 
	            
	        	  
	        	  parent.getId();
	              
	              //System.out.println("list count : " + parent.getCount());
	              //System.out.println(parent.getAdapter());
	              //System.out.println("toString : " + parent.toString());
	              //System.out.println("ass den item gedreckt ginn ??? : " + parent.isPressed());
	              //System.out.println("et ass den item position gedreckt ginn : " + parent.getItemIdAtPosition(position));
	              //System.out.println("den title den ausgewielt ginn ass : " + titleArray[(int) parent.getItemIdAtPosition(position)]);
	              
	              
	              String test =  idArray[((int) parent.getItemIdAtPosition(position))];
	              
	              wickedClient.queueTest(test);	//add selected item to wicked queue
	              
	        } 	//end onItemCkick 
        });		//end listView.setOnItemClickListener
    }			//end listViewQueryResults

    
}	//end class GuiTestActivity